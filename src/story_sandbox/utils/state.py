"""Sandbox state management (sandbox-state.json).

Multi-dimensional relationship model:
    trust, affection, rivalry, fear  (each -100 to 100)
Backward compatible: old int values auto-migrate to {affection: val}.
"""

import json
from pathlib import Path
from typing import Any


class SandboxState:
    """Manages the sandbox-state.json file."""

    # -- Memory archiving thresholds (rounds) --
    MEMORY_FULL_ROUNDS = 5       # 0-5: keep verbatim
    MEMORY_SUMMARY_ROUNDS = 15   # 6-15: compress to summary
    # 16+: archive unless marked significant
    MEMORY_ACTIVE_LIMIT = 15     # max active memories per character

    # -- Relationship dimensions --
    REL_DIMS = ("trust", "affection", "rivalry", "fear")

    def __init__(self, vault_path: Path):
        self.vault_path = vault_path
        self.state_file = vault_path / "sandbox-state.json"
        self._data: dict = {}
        if self.state_file.exists():
            self._load()

    def _load(self):
        self._data = json.loads(self.state_file.read_text(encoding="utf-8"))
        self._migrate_relationships()

    def save(self):
        self.state_file.write_text(
            json.dumps(self._data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    # ------------------------------------------------------------------
    # Migration: int relationships -> multi-dimensional
    # ------------------------------------------------------------------

    def _migrate_relationships(self):
        """Convert legacy int relationships to multi-dimensional dicts."""
        for name, char in self._data.get("characters", {}).items():
            rels = char.get("relationships", {})
            changed = False
            for other, val in list(rels.items()):
                if isinstance(val, (int, float)):
                    rels[other] = self._default_rel(affection=int(val))
                    changed = True
            if changed:
                char.setdefault("archivedMemories", [])
                char.setdefault("traits", {})
                char.setdefault("status", "active")

    # ------------------------------------------------------------------
    # Init
    # ------------------------------------------------------------------

    def init(self, world: dict, target_chapters: int = 30):
        self._data = {
            "version": "1.0.0",
            "currentRound": 0,
            "targetChapters": target_chapters,
            "vaultPath": str(self.vault_path),
            "world": world,
            "characters": {},
            "foreshadowing": [],
            "consistencyLog": [],
            "triggers": [],
            "sceneHistory": [],
            "metadata": {},
        }

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def current_round(self) -> int:
        return self._data.get("currentRound", 0)

    @current_round.setter
    def current_round(self, value: int):
        self._data["currentRound"] = value

    @property
    def target_chapters(self) -> int:
        return self._data.get("targetChapters", 30)

    @property
    def metadata(self) -> dict:
        return self._data.setdefault("metadata", {})

    # ------------------------------------------------------------------
    # Characters
    # ------------------------------------------------------------------

    def add_character(self, name: str, gender: str, personality: list, background: str,
                      motive: str, secret: str, relationships: dict | None = None):
        """Add a character.  relationships values can be int (legacy) or dict."""
        normalized_rels = {}
        for other, val in (relationships or {}).items():
            normalized_rels[other] = self._coerce_rel(val)

        self._data.setdefault("characters", {})[name] = {
            "gender": gender,
            "personality": personality,
            "background": background,
            "motive": motive,
            "secret": secret,
            "status": "active",
            "mood": "\u5e73\u9759",
            "moodCause": "\u521d\u59cb\u72b6\u6001",
            "relationships": normalized_rels,
            "memories": [],
            "archivedMemories": [],
            "traits": {},
            "growth": [],
            "lastActiveRound": 0,
            "roundsSinceActive": 0,
        }

    def get_character(self, name: str) -> dict | None:
        return self._data.get("characters", {}).get(name)

    def update_relationship(self, from_char: str, to_char: str, delta: int | dict):
        """Update relationship.  delta can be int (legacy -> affection) or
        dict with keys trust/affection/rivalry/fear."""
        char = self.get_character(from_char)
        if not char:
            return
        rels = char.setdefault("relationships", {})
        current = rels.get(to_char)
        if current is None or isinstance(current, (int, float)):
            current = self._coerce_rel(current or 0)
        if isinstance(delta, (int, float)):
            current["affection"] = max(-100, min(100, current["affection"] + int(delta)))
        else:
            for dim in self.REL_DIMS:
                if dim in delta:
                    current[dim] = max(-100, min(100, current[dim] + delta[dim]))
        rels[to_char] = current

    # ------------------------------------------------------------------
    # Relationship helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _default_rel(trust=0, affection=0, rivalry=0, fear=0) -> dict:
        return {"trust": trust, "affection": affection, "rivalry": rivalry, "fear": fear}

    def _coerce_rel(self, val) -> dict:
        """Convert legacy int to multi-dimensional dict."""
        if isinstance(val, dict):
            return {dim: val.get(dim, 0) for dim in self.REL_DIMS}
        return self._default_rel(affection=int(val) if val else 0)

    def get_relationship_summary(self, from_char: str, to_char: str) -> float:
        """Weighted summary: trust*0.4 + affection*0.4 - rivalry*0.1 - fear*0.1."""
        char = self.get_character(from_char)
        if not char:
            return 0.0
        rel = char.get("relationships", {}).get(to_char)
        if rel is None:
            return 0.0
        if isinstance(rel, (int, float)):
            return float(rel)
        return (rel.get("trust", 0) * 0.4
                + rel.get("affection", 0) * 0.4
                - rel.get("rivalry", 0) * 0.1
                - rel.get("fear", 0) * 0.1)

    @staticmethod
    def relationship_label(summary: float) -> str:
        """Map weighted summary to a human-readable label."""
        if summary >= 70:
            return "\u631a\u53cb"
        if summary >= 40:
            return "\u4fe1\u4efb"
        if summary >= 15:
            return "\u53cb\u597d"
        if summary >= -15:
            return "\u4e2d\u7acb"
        if summary >= -40:
            return "\u51b7\u6de1"
        if summary >= -70:
            return "\u654c\u5bf9"
        return "\u4ec7\u6068"

    def increment_inactivity(self):
        for name, char in self._data.get("characters", {}).items():
            if char.get("lastActiveRound", 0) < self.current_round:
                char["roundsSinceActive"] = char.get("roundsSinceActive", 0) + 1

    # ------------------------------------------------------------------
    # Memory archiving
    # ------------------------------------------------------------------

    def archive_old_memories(self, current_round: int):
        """Compress/archive old memories per character.

        - 0-5 rounds: keep verbatim
        - 6-15 rounds: compress to summary placeholder
        - 16+ rounds: archive (unless marked significant)
        Active memories capped at MEMORY_ACTIVE_LIMIT.
        """
        for name, char in self._data.get("characters", {}).items():
            memories = char.get("memories", [])
            if not memories:
                continue
            archived = char.setdefault("archivedMemories", [])
            active = []
            for mem in memories:
                age = current_round - mem.get("round", current_round)
                if age <= self.MEMORY_FULL_ROUNDS:
                    active.append(mem)
                elif age <= self.MEMORY_SUMMARY_ROUNDS:
                    active.append({
                        "round": mem.get("round"),
                        "summary": mem.get("summary", mem.get("text", "")[:50]),
                        "archived": False,
                    })
                else:
                    if mem.get("significant"):
                        active.append(mem)
                    else:
                        mem["archived"] = True
                        archived.append(mem)
            if len(active) > self.MEMORY_ACTIVE_LIMIT:
                overflow = active[: len(active) - self.MEMORY_ACTIVE_LIMIT]
                active = active[len(active) - self.MEMORY_ACTIVE_LIMIT:]
                for m in overflow:
                    if not m.get("significant"):
                        m["archived"] = True
                        archived.append(m)
                    else:
                        active.insert(0, m)
            char["memories"] = active

    # ------------------------------------------------------------------
    # Foreshadowing
    # ------------------------------------------------------------------

    def add_foreshadowing(self, text: str, round_num: int, level: str = "B"):
        max_rounds = {"S": 999, "A": 20, "B": 5}.get(level, 5)
        self._data.setdefault("foreshadowing", []).append({
            "id": f"FS-{len(self._data.get('foreshadowing', [])) + 1:03d}",
            "level": level,
            "text": text,
            "plantedRound": round_num,
            "maxRounds": max_rounds,
            "status": "waiting",
        })

    def resolve_foreshadowing(self, text: str):
        for fs in self._data.get("foreshadowing", []):
            if fs["text"] == text or text in fs["text"]:
                fs["status"] = "resolved"

    # ------------------------------------------------------------------
    # Scene history
    # ------------------------------------------------------------------

    def add_scene_history(self, round_num: int, title: str, characters: list, location: str,
                          quality: dict | None = None, scene_type: str | None = None):
        """Record a scene.  quality and scene_type are optional for backward compat."""
        self._data.setdefault("sceneHistory", []).append({
            "round": round_num,
            "title": title,
            "characters": characters,
            "location": location,
            "quality": quality,
            "sceneType": scene_type,
        })

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------

    def get_summary(self, include_memories: bool = True) -> dict:
        chars = {}
        for name, c in self._data.get("characters", {}).items():
            entry = {
                "gender": c.get("gender", "unknown"),
                "status": c.get("status", "active"),
                "mood": c.get("mood", ""),
                "moodCause": c.get("moodCause", ""),
                "relationships": c.get("relationships", {}),
                "lastActiveRound": c.get("lastActiveRound", 0),
                "roundsSinceActive": c.get("roundsSinceActive", 0),
            }
            if include_memories:
                entry["recentMemories"] = c.get("memories", [])[-5:]
            chars[name] = entry

        return {
            "currentRound": self.current_round,
            "targetChapters": self.target_chapters,
            "characters": chars,
            "activeForeshadowing": [
                fs for fs in self._data.get("foreshadowing", [])
                if fs.get("status") == "waiting"
            ],
            "recentScenes": self._data.get("sceneHistory", [])[-10:],
            "progress": f"{self.current_round} rounds / {len(self._data.get('sceneHistory', []))} scenes",
        }

    # ------------------------------------------------------------------
    # Consistency check
    # ------------------------------------------------------------------

    def check_consistency(self, chapter_range: dict | None = None) -> list[dict]:
        """Run consistency checks and return findings."""
        findings = []
        chars = self._data.get("characters", {})

        # 1. Characters with very high inactivity (warning)
        for name, c in chars.items():
            if c.get("roundsSinceActive", 0) >= 5:
                findings.append({
                    "severity": "warning",
                    "type": "character_inactivity",
                    "description": f"{name} has been inactive for {c['roundsSinceActive']} rounds",
                })

        # 2. Inactivity early warning at 3 rounds (info)
        for name, c in chars.items():
            inactive = c.get("roundsSinceActive", 0)
            if 3 <= inactive < 5:
                findings.append({
                    "severity": "info",
                    "type": "character_inactivity_warning",
                    "description": f"{name} has been inactive for {inactive} rounds",
                })

        # 3. Foreshadowing overdue
        for fs in self._data.get("foreshadowing", []):
            if fs["status"] == "waiting":
                age = self.current_round - fs.get("plantedRound", 0)
                max_r = fs.get("maxRounds", 5)
                if age > max_r and fs.get("level") != "S":
                    findings.append({
                        "severity": "warning",
                        "type": "foreshadowing_overdue",
                        "description": f"'{fs['text']}' has been waiting {age} rounds (max: {max_r})",
                    })

        # 4. Relationship value out of bounds (multi-dimensional)
        for name, c in chars.items():
            for other, val in c.get("relationships", {}).items():
                if isinstance(val, dict):
                    for dim, v in val.items():
                        if abs(v) > 100:
                            findings.append({
                                "severity": "warning",
                                "type": "relationship_out_of_bounds",
                                "description": f"{name}->{other} {dim}={v} exceeds [-100,100]",
                            })
                        elif abs(v) > 90:
                            findings.append({
                                "severity": "info",
                                "type": "relationship_extreme",
                                "description": f"{name}->{other} {dim}={v} (near boundary)",
                            })
                elif isinstance(val, (int, float)) and abs(val) > 90:
                    findings.append({
                        "severity": "info",
                        "type": "relationship_extreme",
                        "description": f"{name} <-> {other} at {val} (near boundary)",
                    })

        # 5. Dead/unconscious character in recent scenes (critical)
        # TODO: requires status tracking in write_scene

        # 6. Scene type imbalance (requires sceneType in history)
        # TODO: needs enough scenes with sceneType data

        # 7. Consecutive low quality scenes (requires quality in history)
        # TODO: needs enough scenes with quality data

        return findings

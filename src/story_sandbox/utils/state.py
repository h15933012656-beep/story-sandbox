"""Sandbox state management (sandbox-state.json)."""

import json
from pathlib import Path
from typing import Any


class SandboxState:
    """Manages the sandbox-state.json file."""

    def __init__(self, vault_path: Path):
        self.vault_path = vault_path
        self.state_file = vault_path / "sandbox-state.json"
        self._data: dict = {}
        if self.state_file.exists():
            self._load()

    def _load(self):
        self._data = json.loads(self.state_file.read_text(encoding="utf-8"))

    def save(self):
        self.state_file.write_text(
            json.dumps(self._data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

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

    # ------------------------------------------------------------------
    # Characters
    # ------------------------------------------------------------------

    def add_character(self, name: str, gender: str, personality: list, background: str,
                      motive: str, secret: str, relationships: dict | None = None):
        self._data.setdefault("characters", {})[name] = {
            "gender": gender,
            "personality": personality,
            "background": background,
            "motive": motive,
            "secret": secret,
            "mood": "平静",
            "moodCause": "初始状态",
            "relationships": relationships or {},
            "memories": [],
            "growth": [],
            "lastActiveRound": 0,
            "roundsSinceActive": 0,
        }

    def get_character(self, name: str) -> dict | None:
        return self._data.get("characters", {}).get(name)

    def update_relationship(self, from_char: str, to_char: str, delta: int):
        char = self.get_character(from_char)
        if char:
            current = char.get("relationships", {}).get(to_char, 0)
            char["relationships"][to_char] = max(-100, min(100, current + delta))

    def increment_inactivity(self):
        for name, char in self._data.get("characters", {}).items():
            if char.get("lastActiveRound", 0) < self.current_round:
                char["roundsSinceActive"] = char.get("roundsSinceActive", 0) + 1

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

    def add_scene_history(self, round_num: int, title: str, characters: list, location: str):
        self._data.setdefault("sceneHistory", []).append({
            "round": round_num,
            "title": title,
            "characters": characters,
            "location": location,
        })

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------

    def get_summary(self, include_memories: bool = True) -> dict:
        chars = {}
        for name, c in self._data.get("characters", {}).items():
            entry = {
                "gender": c.get("gender", "unknown"),
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
        """Run basic consistency checks and return findings."""
        findings = []
        chars = self._data.get("characters", {})

        # Check 1: Characters with very high inactivity
        for name, c in chars.items():
            if c.get("roundsSinceActive", 0) >= 5:
                findings.append({
                    "severity": "warning",
                    "type": "character_inactivity",
                    "description": f"{name} has been inactive for {c['roundsSinceActive']} rounds",
                })

        # Check 2: Foreshadowing overdue
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

        # Check 3: Relationship extremes
        for name, c in chars.items():
            for other, val in c.get("relationships", {}).items():
                if abs(val) > 90:
                    findings.append({
                        "severity": "info",
                        "type": "relationship_extreme",
                        "description": f"{name} <-> {other} at {val} (near boundary)",
                    })

        return findings

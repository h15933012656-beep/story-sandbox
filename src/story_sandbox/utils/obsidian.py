"""Obsidian vault file writer."""

import json
import shutil
from pathlib import Path
from datetime import datetime


class ObsidianWriter:
    """Writes formatted markdown and canvas files to an Obsidian vault."""

    def __init__(self, vault_path: Path):
        self.vault = vault_path

    # ------------------------------------------------------------------
    # Vault structure
    # ------------------------------------------------------------------

    def create_vault_structure(self):
        """Create the full vault directory structure."""
        dirs = [
            "00-世界观/地点",
            "00-世界观/组织",
            "00-世界观/规则",
            "00-世界观/历史",
            "01-角色",
            "02-场景",
            "03-时间线",
            "04-关系图",
            "05-状态面板",
            "06-画布",
            "07-素材导出/小说正文",
        ]
        for d in dirs:
            (self.vault / d).mkdir(parents=True, exist_ok=True)

        # Create .obsidian directory
        (self.vault / ".obsidian").mkdir(exist_ok=True)

    # ------------------------------------------------------------------
    # World docs
    # ------------------------------------------------------------------

    def write_world_overview(self, world: dict):
        content = f"""---
type: world_overview
era: "{world['era']}"
core_rule: "{world['core_rule']}"
core_conflict: "{world['core_conflict']}"
mood: "{world['mood']}"
created_round: 0
tags: [world, overview]
---

# 世界总览

## 时代背景
{world['era']}

## 核心规则
{world['core_rule']}

## 核心冲突
{world['core_conflict']}

## 情绪基调
{world['mood']}
"""
        (self.vault / "00-世界观" / "世界总览.md").write_text(content, encoding="utf-8")

    def write_world_doc(self, name: str, doc_type: str, content_text: str):
        content = f"""---
type: {doc_type}
name: "{name}"
created_round: 0
tags: [world]
---

# {name}

{content_text}
"""
        (self.vault / "00-世界观" / f"{name}.md").write_text(content, encoding="utf-8")

    def write_location(self, name: str, round_num: int):
        content = f"""---
type: world_location
name: "{name}"
created_round: {round_num}
created_by: auto
tags: [world, location]
---

# {name}

## 描述
（自动创建，待扩展）

## 事件记录
（待填充）
"""
        path = self.vault / "00-世界观" / "地点" / f"{name}.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    # ------------------------------------------------------------------
    # Character
    # ------------------------------------------------------------------

    def write_character(self, name: str, gender: str, personality: list,
                        background: str, motive: str, secret: str,
                        relationships: dict | None = None):
        rel_lines = ""
        if relationships:
            for other, val in relationships.items():
                rel_lines += f"- [[{other}]]（亲密度：{val}）\n"

        content = f"""---
type: character
name: "{name}"
gender: "{gender}"
mood: "平静"
mood_cause: "初始状态"
round_updated: 0
relationships:
{self._yaml_dict(relationships or {})}
tags: [character, "mood/平静"]
---

# {name}

## 基本信息
- 性格：{'、'.join(personality)}
- 背景：{background}
- 动机：{motive}
- 秘密：{secret}

## 当前状态
- 心情：平静
- 原因：初始状态

## 关系
{rel_lines}

## 记忆

## 成长轨迹
"""
        (self.vault / "01-角色" / f"{name}.md").write_text(content, encoding="utf-8")

    # ------------------------------------------------------------------
    # Scene
    # ------------------------------------------------------------------

    def write_scene(self, round: int, title: str, date: str, location: str,
                    characters: list, emotional_arc: str, narrative: str,
                    key_events: list) -> str:
        """Write a scene file and return its path."""
        filename = f"S{round:03d}-{title}.md"
        char_list = "\n".join(f'  - "[[{c}]]"' for c in characters)
        events = "\n".join(f"- {e}" for e in key_events) if key_events else "- （待补充）"

        content = f"""---
type: scene
round: {round}
title: "{title}"
date: "{date}"
location: "[[{location}]]"
characters:
{char_list}
emotional_arc: "{emotional_arc}"
tags: [scene, "轮次/{round}"]
---

# S{round:03d} - {title}

## 场景正文

{narrative}

## 结构化数据

### 关键事件
{events}
"""
        filepath = self.vault / "02-场景" / filename
        filepath.write_text(content, encoding="utf-8")
        return str(filepath)

    # ------------------------------------------------------------------
    # Chapter
    # ------------------------------------------------------------------

    def write_chapter(self, chapter_num: int, title: str, scene_range: dict,
                      text: str) -> str:
        """Write a chapter file and return its path."""
        filename = f"{chapter_num:02d}-{title}.md"
        scenes = f"S{scene_range['start']:03d}-S{scene_range['end']:03d}"

        content = f"""---
type: chapter
chapter: {chapter_num}
title: "{title}"
scenes: ["{scenes}"]
word_count: {len(text)}
---

# 第{_cn(chapter_num)}章 {title}

{text}
"""
        filepath = self.vault / "07-素材导出" / "小说正文" / filename
        filepath.write_text(content, encoding="utf-8")
        return str(filepath)

    def move_scenes_to_chapter_folder(self, chapter_num: int, start_round: int, end_round: int):
        """Move scene files into the chapter subfolder."""
        folder_name = f"{chapter_num:02d}-{_cn(chapter_num)}章"
        target_dir = self.vault / "02-场景" / folder_name
        target_dir.mkdir(parents=True, exist_ok=True)

        scene_dir = self.vault / "02-场景"
        for r in range(start_round, end_round + 1):
            for f in scene_dir.glob(f"S{r:03d}-*.md"):
                if f.is_file() and f.parent == scene_dir:
                    shutil.move(str(f), str(target_dir / f.name))

    # ------------------------------------------------------------------
    # Graph / Canvas
    # ------------------------------------------------------------------

    def write_graph_config(self):
        config = {
            "collapse-filter": False,
            "search": "path:01-角色/ OR path:00-世界观/",
            "showTags": False,
            "showAttachments": False,
            "hideUnresolved": True,
            "showOrphans": False,
            "collapse-color-groups": False,
            "colorGroups": [
                {"query": "path:01-角色/", "color": {"a": 1, "rgb": 3066993}},
                {"query": "path:00-世界观/地点/", "color": {"a": 1, "rgb": 15105570}},
                {"query": "path:00-世界观/规则/ OR path:00-世界观/世界总览", "color": {"a": 1, "rgb": 10181046}},
            ],
            "collapse-display": False,
            "showArrow": True,
            "textFadeMultiplier": 0,
            "nodeSizeMultiplier": 1.3,
            "lineSizeMultiplier": 1,
            "collapse-forces": False,
            "centerStrength": 0.5,
            "repelStrength": 10,
            "linkStrength": 1,
            "linkDistance": 250,
        }
        graph_path = self.vault / ".obsidian" / "graph.json"
        graph_path.write_text(json.dumps(config, indent=2), encoding="utf-8")

    def update_canvas(self, character_colors: dict | None = None):
        """Generate a story overview canvas with characters and locations."""
        nodes = []
        edges = []
        x_offset = 0

        # Character nodes
        char_dir = self.vault / "01-角色"
        if char_dir.exists():
            for f in sorted(char_dir.glob("*.md")):
                name = f.stem
                color = "5"  # default blue
                if character_colors and name in character_colors:
                    color = character_colors[name]
                nodes.append({
                    "id": f"char-{name}",
                    "type": "text",
                    "text": f"## {name}",
                    "x": x_offset,
                    "y": 0,
                    "width": 200,
                    "height": 60,
                    "color": color,
                })
                x_offset += 250

        # Location nodes
        loc_dir = self.vault / "00-世界观" / "地点"
        x_offset = 0
        if loc_dir.exists():
            for f in sorted(loc_dir.glob("**/*.md")):
                name = f.stem
                nodes.append({
                    "id": f"loc-{name}",
                    "type": "text",
                    "text": name,
                    "x": x_offset,
                    "y": 300,
                    "width": 140,
                    "height": 50,
                    "color": "3",
                })
                x_offset += 180

        canvas = {"nodes": nodes, "edges": edges}
        canvas_path = self.vault / "06-画布" / "故事全景.canvas"
        canvas_path.write_text(json.dumps(canvas, indent=2, ensure_ascii=False), encoding="utf-8")

    # ------------------------------------------------------------------
    # Dashboard
    # ------------------------------------------------------------------

    def write_dashboard(self):
        content = """---
type: dashboard
updated_round: 0
---

# 故事状态面板

## 角色状态总览

```dataview
TABLE WITHOUT ID
  file.link AS "角色",
  mood AS "心情",
  mood_cause AS "原因",
  round_updated AS "更新轮次"
FROM "01-角色"
WHERE type = "character"
SORT name ASC
```

## 最近场景

```dataview
TABLE WITHOUT ID
  file.link AS "场景",
  round AS "轮次",
  location AS "地点",
  emotional_arc AS "情绪弧"
FROM "02-场景"
WHERE type = "scene"
SORT round DESC
LIMIT 10
```

## 世界观文档

```dataview
TABLE WITHOUT ID
  file.link AS "文档",
  type AS "类型",
  created_round AS "创建轮次"
FROM "00-世界观"
WHERE type != "world_overview"
SORT type ASC
```
"""
        (self.vault / "05-状态面板" / "面板.md").write_text(content, encoding="utf-8")

    # ------------------------------------------------------------------
    # Export
    # ------------------------------------------------------------------

    def export_novel(self, state) -> str:
        """Export story materials for story-long-write integration."""
        export_dir = self.vault / "07-素材导出" / f"export-{datetime.now().strftime('%Y%m%d')}"
        export_dir.mkdir(parents=True, exist_ok=True)

        # Copy character sheets
        char_export = export_dir / "角色设定"
        char_export.mkdir(exist_ok=True)
        char_dir = self.vault / "01-角色"
        if char_dir.exists():
            for f in char_dir.glob("*.md"):
                shutil.copy2(str(f), str(char_export / f.name))

        # Copy world docs
        world_export = export_dir / "世界观"
        world_export.mkdir(exist_ok=True)
        world_dir = self.vault / "00-世界观"
        if world_dir.exists():
            for f in world_dir.glob("**/*.md"):
                if f.is_file():
                    rel = f.relative_to(world_dir)
                    target = world_export / rel
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(str(f), str(target))

        # Generate outline from scene history
        outline_lines = ["# 剧情大纲\n"]
        for scene in state._data.get("sceneHistory", []):
            outline_lines.append(f"- 第{scene['round']}轮: {scene['title']} ({', '.join(scene['characters'])})")
        (export_dir / "剧情大纲.md").write_text("\n".join(outline_lines), encoding="utf-8")

        return str(export_dir)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _yaml_dict(d: dict) -> str:
        lines = []
        for k, v in d.items():
            lines.append(f'  "{k}": {v}')
        return "\n".join(lines) if lines else "  {}"


def _cn(n: int) -> str:
    """Convert integer to Chinese numeral."""
    nums = "零一二三四五六七八九"
    if n <= 10:
        return nums[n] if n > 0 else "零"
    if n < 20:
        return f"十{nums[n-10]}" if n > 10 else "十"
    tens = n // 10
    ones = n % 10
    result = f"{nums[tens]}十"
    if ones:
        result += nums[ones]
    return result

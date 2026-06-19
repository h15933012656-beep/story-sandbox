# story-sandbox

[English](README.md) | [中文](README_zh-CN.md)

**Autonomous story generation sandbox for Claude.** Set up a world and characters, then watch them develop on their own. Stories are unpredictable — even you don't know what happens next.

Output goes directly to your Obsidian vault with full visualization: relationship graphs, timelines, Dataview dashboards, and Canvas story maps.

---

## What it does

```
You set:   World rules + Characters + Target length
                    ↓
Sandbox:   Characters act autonomously (limited perspective = emergence)
           World self-heals (plot holes get explained, not deleted)
           New locations/characters appear naturally
                    ↓
Output:    Obsidian vault with scenes, chapters, relationship graphs
```

## Install

```bash
pip install story-sandbox
```

Then add to your Claude config:

```json
{
  "mcpServers": {
    "story-sandbox": {
      "command": "story-sandbox"
    }
  }
}
```

Or use the Claude Code CLI:

```bash
claude mcp add story-sandbox -- story-sandbox
```

## Quick start

Open Claude Code and say:

```
Start a story sandbox
```

Claude will guide you through:
1. **Setting up the world** (4 questions: era, rule, conflict, mood)
2. **Creating characters** (name, gender, personality, background, motive, secret)
3. **Choosing target length** (short / medium / long)
4. **Choosing autonomy mode** (full / semi / constrained)
5. **Running the simulation** (characters act on their own)

## Tools

| Tool | Description |
|------|-------------|
| `sandbox_init` | Initialize vault with directory structure and world docs |
| `sandbox_add_character` | Add a character with personality, background, secret |
| `sandbox_get_state` | Read current sandbox state (characters, foreshadowing, scenes) |
| `sandbox_write_scene` | Write a scene file and update character states |
| `sandbox_compile_chapter` | Compile scenes into a novel chapter |
| `sandbox_update_graph` | Update Obsidian Canvas with character-location relationships |
| `sandbox_check_consistency` | Scan for naming conflicts, timeline issues, relationship drift |
| `sandbox_export` | Export materials for story-long-write integration |

## How it works

### Emergence through limited perspective

Each character only knows what they should know — not other characters' inner thoughts, secrets, or unseen events. This creates natural misunderstandings, misjudgments, and unexpected conflicts.

### Self-healing world

When a character encounters an undefined location or concept, the system automatically creates it. When inconsistencies are detected, they're explained rather than deleted ("the memory was tampered with").

### Convergence curve

| Phase | Progress | Behavior |
|-------|----------|----------|
| Free growth | 0-30% | High foreshadowing density. New characters/locations frequent. |
| Recovery | 30-70% | Foreshadowing recovery priority rises. No new S-level foreshadowing. |
| Focus | 70-90% | Foreshadowing only decreases. Characters focus on core conflict. |
| Endgame | 90-100% | All S-level foreshadowing must resolve. Final confrontations. |

### Three foreshadowing levels

| Level | Lifetime | Purpose |
|-------|----------|---------|
| S (story) | Entire book | Core mysteries that span the whole story |
| A (arc) | 10-20 rounds | Mid-level mysteries resolved per arc |
| B (scene) | 3-5 rounds | Small hooks for immediate engagement |

---

## Obsidian integration

The sandbox outputs everything directly into an Obsidian vault. Open the vault in Obsidian and the story comes alive with interactive visualization.

### Required plugins

| Plugin | Required | Purpose |
|--------|----------|---------|
| **Dataview** | Yes | Powers the status dashboard (character states, scene timeline, foreshadowing tracker) |
| **Canvas** | Built-in | Story map with characters, locations, and relationships |
| **Graph View** | Built-in | Relationship network between characters and locations |

Install Dataview from Settings → Community Plugins → Browse → search "Dataview" → Install → Enable.

### Vault structure

```
your-vault/
├── 00-世界观/                  World documents
│   ├── 世界总览.md             World overview (era, rule, conflict, mood)
│   ├── 核心规则.md             Core rule of this world
│   ├── 核心冲突.md             Core conflict
│   ├── 地点/                   Locations (auto-created as characters explore)
│   │   ├── 渊城/               City → district → specific location
│   │   │   ├── 老城区/
│   │   │   │   └── 默记书店.md
│   │   │   └── 中心区/
│   │   │       └── 档案馆.md
│   │   └── 南昌/
│   │       └── 养老社区.md
│   ├── 组织/                   Organizations
│   ├── 规则/                   World rules
│   └── 历史/                   Historical events
│
├── 01-角色/                    Character sheets (updated every round)
│   ├── 林默.md                 Frontmatter: mood, relationships, round_updated
│   ├── 苏晴.md                 Body: personality, background, memory log, growth
│   └── ...
│
├── 02-场景/                    Scenes organized by chapter
│   ├── 01-第一章/
│   │   ├── S001-雨夜来客.md    Each scene: narrative + structured data
│   │   ├── S002-南郊旧影.md
│   │   └── ...
│   ├── 02-第二章/
│   └── ...
│
├── 03-时间线/
│   └── 时间线.md               Full timeline by chapter
│
├── 04-关系图/
│   └── 关系索引.md             One card per character with relationship details
│
├── 05-状态面板/
│   └── 面板.md                 Dataview dashboard (auto-refreshing)
│
├── 06-画布/
│   └── 故事全景.canvas         Canvas story map
│
├── 07-素材导出/
│   └── 小说正文/               Compiled novel chapters
│       ├── 01-旧地图.md
│       ├── 02-拼图.md
│       └── ...
│
└── sandbox-state.json          Machine-readable state (characters, foreshadowing, etc.)
```

### Graph View

The Graph View shows **characters and locations only** (scenes excluded to prevent clutter). Color-coded:

| Color | Category | Example |
|-------|----------|---------|
| Green | Characters | Lin Mo, Su Qing, Chen Wei |
| Orange | Locations | Bookstore, Archive, Safe house |
| Purple | World rules | Ability cost, Core rule |

Characters connect to locations they visit, and to other characters through wikilinks. The graph updates automatically as the story develops.

### Dataview dashboard

The `05-状态面板/面板.md` file contains auto-refreshing Dataview queries:

- **Character status table** — mood, cause, last updated round for each character
- **Recent scenes** — last 10 scenes with round number, location, and emotional arc
- **World documents** — all world-building docs with type and creation round

### Relationship cards

The `04-关系图/关系索引.md` file uses a per-character card format (not a matrix):

```markdown
## Lin Mo

- **Su Qing** — 75 trust. Alliance partner, both investigated the corruption together.
- **Chen Wei** — -30 hostile. Confirmed as the one who blocked his identity.
- **Fang Yuan** — 40 cooperation. Met secretly at Half-Cup Teahouse.

## Relationship timeline

### Lin Mo <-> Su Qing: from strangers to allies
Round 1 stranger → Round 2 testing → Round 11 alliance → Round 15 fighting together
```

### Canvas story map

The `06-画布/故事全景.canvas` file creates an interactive story map:

- **Character nodes** (top) — color-coded by alignment (blue=protagonist, red=antagonist, yellow=gray)
- **Location nodes** (bottom) — all significant places
- **Edges** — labeled with relationship values ("alliance 75", "hostile -30")
- **Story overview node** — current arc and progress

Open the canvas file in Obsidian to drag, zoom, and explore the story structure.

### Scene files

Each scene file in `02-场景/` contains:

```markdown
---
type: scene
round: 5
title: "深夜来电"
date: "2026-06-20"
location: "[[默记书店]]"
characters: ["[[林默]]", "[[苏晴]]"]
emotional_arc: "平静 -> 紧张 -> 释放"
tags: [scene, "轮次/5"]
---

# S005 - 深夜来电

## 场景正文
{200-800 word narrative}

## 结构化数据
### 关键事件
- Event 1
- Event 2
### 关系变化
- [[林默]] <-> [[苏晴]]：信任加深（亲密度 +10）
### 伏笔
- 新增：...
- 回收：...
```

All wikilinks (`[[...]]`) create connections in Graph View automatically.

---

## Example

A story about a near-future city where everyone has abilities but using them shortens lifespan:

```
World:  Near-future city, abilities shorten lifespan,
        Bureau vs Liberation Organization, dark mood
Characters:
  - Lin Mo (male): Ex-agent, bookstore owner, looking for missing sister
  - Su Qing (female): Investigative journalist, ability: read memories by touch
  - Chen Wei (male): Entrepreneur, secretly behind the sister's disappearance
```

After 50 rounds of autonomous development:
- 50 scenes across 10 chapters
- 7 characters (3 original + 4 emerged)
- 13 locations across 2 cities
- ~40,000 Chinese characters of novel text
- Complete relationship graph and timeline

## Requirements

- Python 3.10+
- Claude Code or Claude Desktop
- Obsidian with [Dataview](https://github.com/blacksmithgu/obsidian-dataview) plugin

## License

MIT

# story-sandbox

**Autonomous story generation sandbox for Claude.** Set up a world and characters, then watch them develop on their own. Stories are unpredictable — even you don't know what happens next.

Output goes directly to your Obsidian vault with full visualization: relationship graphs, timelines, Dataview dashboards, and Canvas story maps.

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
启动沙盒
```

Or in English:

```
Start a story sandbox
```

Claude will guide you through:
1. **Setting up the world** (4 questions: era, rule, conflict, mood)
2. **Creating characters** (name, gender, personality, background, motive, secret)
3. **Choosing autonomy mode** (full / semi / constrained)
4. **Running the simulation** (characters act on their own)

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

```
0-30%   Free growth. High foreshadowing density. New characters/locations frequent.
30-70%  Foreshadowing recovery priority rises. No new S-level foreshadowing.
70-90%  Foreshadowing only decreases. Characters focus on core conflict.
90-100% All S-level foreshadowing must resolve. Final confrontations.
```

### Three foreshadowing levels

| Level | Lifetime | Purpose |
|-------|----------|---------|
| S (story) | Entire book | Core mysteries that span the whole story |
| A (arc) | 10-20 rounds | Mid-level mysteries resolved per arc |
| B (scene) | 3-5 rounds | Small hooks for immediate engagement |

## Obsidian output

```
your-vault/
├── 00-世界观/          World docs (auto-expanded)
├── 01-角色/            Character sheets (updated each round)
├── 02-场景/
│   ├── 01-第一章/      Scenes organized by chapter
│   └── ...
├── 03-时间线/          Timeline index
├── 04-关系图/          Relationship cards (one per character)
├── 05-状态面板/        Dataview dashboard
├── 06-画布/            Canvas story map
├── 07-素材导出/
│   └── 小说正文/       Novel chapters (01-xxx.md, 02-xxx.md)
└── sandbox-state.json
```

### Graph View colors

| Color | Category |
|-------|----------|
| Green | Characters |
| Orange | Locations |
| Purple | World rules |

Scenes are excluded from Graph View to prevent clutter.

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

After 50 rounds of autonomous development, the sandbox produced:
- 50 scenes across 10 chapters
- 7 characters (3 original + 4 emerged)
- 13 locations across 2 cities
- ~40,000 Chinese characters of novel text
- Complete relationship graph and timeline

## Requirements

- Python 3.10+
- Claude Code or Claude Desktop
- Obsidian (with Dataview plugin for dashboard)

## License

MIT

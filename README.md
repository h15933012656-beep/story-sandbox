# story-sandbox

**自主故事生成沙盒 / Autonomous story generation sandbox for Claude**

设定世界观和角色，然后看着他们自己发展。故事不可预测 — 连你都不知道接下来会发生什么。

Set up a world and characters, then watch them develop on their own. Stories are unpredictable — even you don't know what happens next.

输出到 Obsidian vault，自动生成关系图谱、时间线、Dataview 面板和 Canvas 画布。

Output goes directly to your Obsidian vault with full visualization: relationship graphs, timelines, Dataview dashboards, and Canvas story maps.

---

## 工作原理 / How it works

```
你设定：  世界观 + 角色 + 目标长度
You set:  World rules + Characters + Target length
              ↓
沙盒运行：角色自主行动（有限视角 = 涌现）
Sandbox:  Characters act autonomously (limited perspective = emergence)
          世界自我修补（漏洞被解释，而非删除）
          World self-heals (plot holes get explained, not deleted)
          新地点/角色自然出现
          New locations/characters appear naturally
              ↓
输出：    Obsidian vault（场景、章节、关系图谱）
Output:   Obsidian vault with scenes, chapters, relationship graphs
```

---

## 安装 / Install

```bash
pip install story-sandbox
```

然后添加到 Claude 配置 / Then add to your Claude config:

```json
{
  "mcpServers": {
    "story-sandbox": {
      "command": "story-sandbox"
    }
  }
}
```

或使用 Claude Code CLI / Or use the Claude Code CLI:

```bash
claude mcp add story-sandbox -- story-sandbox
```

---

## 快速开始 / Quick start

打开 Claude Code 说 / Open Claude Code and say:

```
启动沙盒
```

```
Start a story sandbox
```

Claude 会引导你完成 / Claude will guide you through:

1. **设定世界观**（4 个问题：时代、规则、冲突、基调）/ **Setting up the world** (4 questions: era, rule, conflict, mood)
2. **创建角色**（姓名、性别、性格、背景、动机、秘密）/ **Creating characters** (name, gender, personality, background, motive, secret)
3. **选择自主模式**（完全/半/约束）/ **Choosing autonomy mode** (full / semi / constrained)
4. **运行模拟**（角色自己行动）/ **Running the simulation** (characters act on their own)

---

## 工具 / Tools

| 工具 / Tool | 说明 / Description |
|-------------|-------------------|
| `sandbox_init` | 初始化 vault 目录结构和世界文档 / Initialize vault with directory structure and world docs |
| `sandbox_add_character` | 添加角色（性格、背景、秘密）/ Add a character with personality, background, secret |
| `sandbox_get_state` | 读取当前状态（角色、伏笔、场景）/ Read current sandbox state (characters, foreshadowing, scenes) |
| `sandbox_write_scene` | 写入场景文件并更新角色状态 / Write a scene file and update character states |
| `sandbox_compile_chapter` | 编译场景为小说章节 / Compile scenes into a novel chapter |
| `sandbox_update_graph` | 更新 Obsidian Canvas 人物-地点关系图 / Update Obsidian Canvas with character-location relationships |
| `sandbox_check_consistency` | 扫描命名冲突、时间线问题、关系漂移 / Scan for naming conflicts, timeline issues, relationship drift |
| `sandbox_export` | 导出素材供 story-long-write 使用 / Export materials for story-long-write integration |

---

## 核心机制 / Core mechanics

### 有限视角涌现 / Emergence through limited perspective

每个角色只知道该知道的事 — 不知道其他角色的内心、秘密或未目击的事件。这自然产生误解、误判和意外冲突。

Each character only knows what they should know — not other characters' inner thoughts, secrets, or unseen events. This creates natural misunderstandings, misjudgments, and unexpected conflicts.

### 世界自我修补 / Self-healing world

角色遇到未定义的地点或概念时，系统自动创建。发现不一致时，解释而非删除（"那段记忆被篡改了"）。

When a character encounters an undefined location or concept, the system automatically creates it. When inconsistencies are detected, they're explained rather than deleted ("the memory was tampered with").

### 收敛曲线 / Convergence curve

```
0-30%   自由生长，伏笔密度高
        Free growth. High foreshadowing density.
30-70%  伏笔回收优先级上升，不再新增 S 级伏笔
        Foreshadowing recovery priority rises. No new S-level foreshadowing.
70-90%  伏笔只减不增，角色聚焦核心冲突
        Foreshadowing only decreases. Characters focus on core conflict.
90-100% 所有 S 级伏笔必须回收，最终对决
        All S-level foreshadowing must resolve. Final confrontations.
```

### 伏笔三级系统 / Three foreshadowing levels

| 等级 / Level | 生命周期 / Lifetime | 用途 / Purpose |
|--------------|---------------------|---------------|
| S（故事级） | 整本书 / Entire book | 贯穿全书的核心悬念 / Core mysteries that span the whole story |
| A（篇章级） | 10-20 轮 / 10-20 rounds | 每个篇章解决的中等悬念 / Mid-level mysteries resolved per arc |
| B（场景级） | 3-5 轮 / 3-5 rounds | 即时钩子 / Small hooks for immediate engagement |

---

## Obsidian 输出结构 / Obsidian output

```
your-vault/
├── 00-世界观/          世界文档（自动扩展）/ World docs (auto-expanded)
├── 01-角色/            角色卡（每轮更新）/ Character sheets (updated each round)
├── 02-场景/
│   ├── 01-第一章/      按章节分类 / Scenes organized by chapter
│   └── ...
├── 03-时间线/          时间线索引 / Timeline index
├── 04-关系图/          关系卡片（每人一张）/ Relationship cards (one per character)
├── 05-状态面板/        Dataview 面板 / Dataview dashboard
├── 06-画布/            Canvas 故事地图 / Canvas story map
├── 07-素材导出/
│   └── 小说正文/       章节正文 / Novel chapters (01-xxx.md, 02-xxx.md)
└── sandbox-state.json
```

### 图谱颜色 / Graph View colors

| 颜色 / Color | 分类 / Category |
|-------------|----------------|
| 绿色 / Green | 角色 / Characters |
| 橙色 / Orange | 地点 / Locations |
| 紫色 / Purple | 世界规则 / World rules |

场景不参与图谱，避免过于拥挤。场景间关系通过时间线文件追踪。

Scenes are excluded from Graph View to prevent clutter. Scene relationships are tracked via timeline files.

---

## 示例 / Example

一个近未来都市的故事，人人有异能但使用会缩短寿命：

A story about a near-future city where everyone has abilities but using them shortens lifespan:

```
世界 / World:
  近未来都市，异能缩短寿命
  Near-future city, abilities shorten lifespan
  异能管理局 vs 异能解放组织
  Bureau vs Liberation Organization
  阴郁、压抑
  Dark, oppressive mood

角色 / Characters:
  林默（男）：前特工，书店老板，找失踪妹妹
  Lin Mo (male): Ex-agent, bookstore owner, looking for missing sister

  苏晴（女）：调查记者，异能：触碰读取记忆
  Su Qing (female): Investigative journalist, ability: read memories by touch

  陈维（男）：企业家，妹妹失踪的幕后黑手
  Chen Wei (male): Entrepreneur, secretly behind the sister's disappearance
```

经过 50 轮自主发展后：

After 50 rounds of autonomous development:

- 50 个场景，10 章小说 / 50 scenes across 10 chapters
- 7 个角色（3 个初始 + 4 个涌现）/ 7 characters (3 original + 4 emerged)
- 13 个地点，2 个城市 / 13 locations across 2 cities
- ~40,000 中文字 / ~40,000 Chinese characters
- 完整关系图谱和时间线 / Complete relationship graph and timeline

---

## 环境要求 / Requirements

- Python 3.10+
- Claude Code 或 Claude Desktop / or Claude Desktop
- Obsidian（需安装 Dataview 插件）/ with Dataview plugin for dashboard

## 许可证 / License

MIT

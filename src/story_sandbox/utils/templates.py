"""Template loading utilities and genre presets."""

from pathlib import Path

# templates/ is at project root: story-sandbox-mcp/templates/
# __file__  = story-sandbox-mcp/src/story_sandbox/utils/templates.py
# .parent x2 = story-sandbox-mcp/src/story_sandbox/.. = story-sandbox-mcp
TEMPLATE_DIR = Path(__file__).parent.parent.parent / "templates"


def load_template(name: str) -> str:
    """Load a template file by name."""
    path = TEMPLATE_DIR / name
    if path.exists():
        return path.read_text(encoding="utf-8")
    return ""


# ---------------------------------------------------------------------------
# Genre presets
# ---------------------------------------------------------------------------

GENRE_PRESETS: dict[str, dict] = {
    "xuanhuan": {
        "label": "玄幻",
        "world_defaults": {
            "core_rule": "天地灵气充盈，修炼可超脱凡俗，实力境界分明（炼气→筑基→金丹→元婴→化神→渡劫）",
            "mood": "热血、宏大、充满机遇与危险",
        },
        "character_tendencies": {
            "action_bias": "修炼、战斗、争夺机缘",
            "growth_axis": "境界突破、功法领悟、心魔克服",
        },
        "narrative_style": "气势磅礴，战斗描写细腻，注重实力对比和逆转感",
    },
    "xianxia": {
        "label": "仙侠",
        "world_defaults": {
            "core_rule": "仙凡有别，修仙求长生，但天道无情，因果循环",
            "mood": "飘逸、沧桑、带有一丝宿命感",
        },
        "character_tendencies": {
            "action_bias": "历练、悟道、了结因果",
            "growth_axis": "心境突破、仙缘际遇、对天道的感悟",
        },
        "narrative_style": "意境深远，善于自然景物描写，情感内敛但厚重",
    },
    "urban": {
        "label": "都市",
        "world_defaults": {
            "core_rule": "现代社会表面平静，暗流涌动；主角拥有特殊能力或身份",
            "mood": "现代感、节奏明快、时而紧张时而轻松",
        },
        "character_tendencies": {
            "action_bias": "职场博弈、人际周旋、暗中布局",
            "growth_axis": "社会地位提升、人脉积累、秘密逐步揭露",
        },
        "narrative_style": "对话驱动，节奏紧凑，善用都市细节营造真实感",
    },
    "scifi": {
        "label": "科幻",
        "world_defaults": {
            "core_rule": "科技高度发达，但技术进步带来新的伦理困境和社会矛盾",
            "mood": "冷峻、理性、充满对未来的思考",
        },
        "character_tendencies": {
            "action_bias": "探索未知、技术突破、伦理抉择",
            "growth_axis": "认知突破、技术能力、对人性的理解",
        },
        "narrative_style": "逻辑严密，技术描写精确，善用推演和反转",
    },
    "fantasy": {
        "label": "奇幻",
        "world_defaults": {
            "core_rule": "魔法或超自然力量与文明交织，种族多元，古老预言牵引命运",
            "mood": "史诗感、神秘、充满未知",
        },
        "character_tendencies": {
            "action_bias": "冒险、探索、对抗古老邪恶",
            "growth_axis": "力量觉醒、种族认同、命运抗争",
        },
        "narrative_style": "世界观宏大，善用意象和隐喻，史诗叙事与个人成长交织",
    },
    "horror": {
        "label": "悬疑/恐怖",
        "world_defaults": {
            "core_rule": "表象之下隐藏真相，每个线索都可能是陷阱；恐惧源于未知",
            "mood": "压抑、紧张、步步逼近的不安",
        },
        "character_tendencies": {
            "action_bias": "调查真相、破解谜团、在恐惧中保持理性",
            "growth_axis": "心理承受力、洞察力、对真相的接受",
        },
        "narrative_style": "氛围渲染优先，节奏张弛有度，善用细节暗示和信息差制造悬念",
    },
}


def load_genre_template(genre: str) -> dict | None:
    """Load a genre preset by key. Returns None if genre not found."""
    return GENRE_PRESETS.get(genre)

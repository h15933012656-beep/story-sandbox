"""
story-sandbox: Autonomous story generation sandbox for Claude.

Characters develop on their own, world self-heals, output to Obsidian vault.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from .utils.state import SandboxState
from .utils.obsidian import ObsidianWriter
from .utils.templates import load_template, load_genre_template

# ---------------------------------------------------------------------------
# Server setup
# ---------------------------------------------------------------------------

app = Server("story-sandbox")

def _ok(msg: str, data: dict | None = None) -> list[TextContent]:
    """Return a success text result."""
    payload = {"status": "ok", "message": msg}
    if data:
        payload["data"] = data
    return [TextContent(type="text", text=json.dumps(payload, ensure_ascii=False, indent=2))]

def _err(msg: str) -> list[TextContent]:
    return [TextContent(type="text", text=json.dumps({"status": "error", "message": msg}, ensure_ascii=False))]


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------

@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="sandbox_init",
            description="Initialize a new story sandbox vault with directory structure, world docs, and graph config. Call this first.",
            inputSchema={
                "type": "object",
                "properties": {
                    "vault_path": {"type": "string", "description": "Absolute path to the Obsidian vault directory"},
                    "genre": {
                        "type": "string",
                        "enum": ["xuanhuan", "xianxia", "urban", "scifi", "fantasy", "horror", "custom"],
                        "description": "Story genre preset (default: custom). Loads genre-specific default values for core_rule and narrative style.",
                        "default": "custom",
                    },
                    "world": {
                        "type": "object",
                        "properties": {
                            "era": {"type": "string", "description": "Time period (e.g. 'near-future city')"},
                            "core_rule": {"type": "string", "description": "The one unique rule of this world"},
                            "core_conflict": {"type": "string", "description": "The fundamental conflict driving the story"},
                            "mood": {"type": "string", "description": "Emotional tone (e.g. 'dark, oppressive, occasionally hot-blooded')"},
                        },
                        "required": ["era", "core_rule", "core_conflict", "mood"],
                    },
                    "target_chapters": {"type": "integer", "description": "Target number of chapters (default 30)", "default": 30},
                },
                "required": ["vault_path", "world"],
            },
        ),
        Tool(
            name="sandbox_add_character",
            description="Add a character to the sandbox. Creates a character sheet file in 01-角色/ and updates sandbox-state.json.",
            inputSchema={
                "type": "object",
                "properties": {
                    "vault_path": {"type": "string"},
                    "name": {"type": "string", "description": "Character name"},
                    "gender": {"type": "string", "enum": ["male", "female"], "description": "Gender (used for pronouns in chapter compilation)"},
                    "personality": {"type": "array", "items": {"type": "string"}, "description": "3-5 personality keywords"},
                    "background": {"type": "string", "description": "One-sentence backstory"},
                    "motive": {"type": "string", "description": "What the character wants most right now"},
                    "secret": {"type": "string", "description": "Something they hide; revelation would change the plot"},
                    "initial_relationships": {
                        "type": "object",
                        "additionalProperties": {
                            "type": "object",
                            "properties": {
                                "trust": {"type": "integer", "description": "信任度 (-100 to 100)"},
                                "affection": {"type": "integer", "description": "好感度 (-100 to 100)"},
                                "rivalry": {"type": "integer", "description": "竞争度 (-100 to 100)"},
                                "fear": {"type": "integer", "description": "畏惧度 (-100 to 100)"},
                            },
                        },
                        "description": "Map of character_name -> {trust?, affection?, rivalry?, fear?}",
                    },
                },
                "required": ["vault_path", "name", "gender", "personality", "background", "motive", "secret"],
            },
        ),
        Tool(
            name="sandbox_get_state",
            description="Read the current sandbox state: round number, all characters, foreshadowing, scene history. Returns a compact summary suitable for feeding into story generation prompts.",
            inputSchema={
                "type": "object",
                "properties": {
                    "vault_path": {"type": "string"},
                    "include_memories": {"type": "boolean", "description": "Include last 5 memories per character (default true)", "default": True},
                },
                "required": ["vault_path"],
            },
        ),
        Tool(
            name="sandbox_write_scene",
            description="Write a scene file to the vault. The scene narrative and metadata are written to 02-场景/. Also updates character files, sandbox-state.json, and timeline.",
            inputSchema={
                "type": "object",
                "properties": {
                    "vault_path": {"type": "string"},
                    "round": {"type": "integer"},
                    "title": {"type": "string", "description": "4-8 character scene title"},
                    "date": {"type": "string", "description": "In-story date (YYYY-MM-DD)"},
                    "location": {"type": "string", "description": "Location name (wikilink target)"},
                    "characters": {"type": "array", "items": {"type": "string"}, "description": "Character names present"},
                    "emotional_arc": {"type": "string", "description": "e.g. 'calm -> tense -> release'"},
                    "narrative": {"type": "string", "description": "200-800 word narrative text"},
                    "key_events": {"type": "array", "items": {"type": "string"}},
                    "relationship_changes": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "from_char": {"type": "string"},
                                "to_char": {"type": "string"},
                                "delta": {
                                    "description": "Integer (legacy -> affection) or object {trust?, affection?, rivalry?, fear?}",
                                    "oneOf": [
                                        {"type": "integer"},
                                        {
                                            "type": "object",
                                            "properties": {
                                                "trust": {"type": "integer"},
                                                "affection": {"type": "integer"},
                                                "rivalry": {"type": "integer"},
                                                "fear": {"type": "integer"},
                                            },
                                        },
                                    ],
                                },
                                "reason": {"type": "string"},
                            },
                        },
                    },
                    "quality": {
                        "type": "object",
                        "description": "Scene quality scores, e.g. {pacing: 8, dialogue: 7, tension: 9, overall: 8}",
                        "additionalProperties": {"type": "number"},
                    },
                    "scene_type": {
                        "type": "string",
                        "enum": ["action", "dialogue", "transition", "climax", "opening", "ending", "flashback"],
                        "description": "Scene type for balance tracking",
                    },
                    "foreshadowing_add": {"type": "array", "items": {"type": "string"}},
                    "foreshadowing_resolve": {"type": "array", "items": {"type": "string"}},
                    "new_locations": {"type": "array", "items": {"type": "string"}, "description": "New location names to auto-create"},
                },
                "required": ["vault_path", "round", "title", "narrative", "characters"],
            },
        ),
        Tool(
            name="sandbox_compile_chapter",
            description="Read the last N scene files and compile them into a chapter file in 07-素材导出/小说正文/. Returns the chapter text. Also moves scene files into the correct chapter subfolder.",
            inputSchema={
                "type": "object",
                "properties": {
                    "vault_path": {"type": "string"},
                    "chapter_number": {"type": "integer"},
                    "chapter_title": {"type": "string"},
                    "scene_range": {
                        "type": "object",
                        "properties": {
                            "start": {"type": "integer", "description": "First scene round number"},
                            "end": {"type": "integer", "description": "Last scene round number"},
                        },
                        "required": ["start", "end"],
                    },
                    "narrative_text": {"type": "string", "description": "The compiled chapter text (3000-4000 chars)"},
                },
                "required": ["vault_path", "chapter_number", "chapter_title", "scene_range", "narrative_text"],
            },
        ),
        Tool(
            name="sandbox_update_graph",
            description="Update the Obsidian Canvas file (故事全景.canvas) with current character and location nodes and their relationships.",
            inputSchema={
                "type": "object",
                "properties": {
                    "vault_path": {"type": "string"},
                    "character_colors": {
                        "type": "object",
                        "additionalProperties": {"type": "string"},
                        "description": "Map of character_name -> color ('5'=blue/good, '1'=red/bad, '6'=yellow/gray, '4'=purple/trapped)",
                    },
                },
                "required": ["vault_path"],
            },
        ),
        Tool(
            name="sandbox_check_consistency",
            description="Run a consistency check on recent scenes. Scans for naming conflicts, relationship drift, timeline issues, and AI writing patterns. Returns a list of findings.",
            inputSchema={
                "type": "object",
                "properties": {
                    "vault_path": {"type": "string"},
                    "chapter_range": {
                        "type": "object",
                        "properties": {
                            "start": {"type": "integer"},
                            "end": {"type": "integer"},
                        },
                    },
                },
                "required": ["vault_path"],
            },
        ),
        Tool(
            name="sandbox_export",
            description="Export story materials for story-long-write integration. Generates outline, character sheets, world docs, and highlight scenes.",
            inputSchema={
                "type": "object",
                "properties": {
                    "vault_path": {"type": "string"},
                },
                "required": ["vault_path"],
            },
        ),
        Tool(
            name="sandbox_set_budget",
            description="Set or update budget metadata (e.g. target_words, daily_quota, deadline). Stores in sandbox-state.json metadata.",
            inputSchema={
                "type": "object",
                "properties": {
                    "vault_path": {"type": "string"},
                    "target_words": {"type": "integer", "description": "Total target word count for the novel"},
                    "daily_quota": {"type": "integer", "description": "Daily writing quota in words"},
                    "deadline": {"type": "string", "description": "Deadline date (YYYY-MM-DD)"},
                    "chapter_budget": {"type": "integer", "description": "Target word count per chapter"},
                },
                "required": ["vault_path"],
            },
        ),
        Tool(
            name="sandbox_get_budget",
            description="Get current budget status: target, progress, remaining words, and daily pacing.",
            inputSchema={
                "type": "object",
                "properties": {
                    "vault_path": {"type": "string"},
                },
                "required": ["vault_path"],
            },
        ),
    ]


# ---------------------------------------------------------------------------
# Tool handlers
# ---------------------------------------------------------------------------

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    try:
        if name == "sandbox_init":
            return await _handle_init(arguments)
        elif name == "sandbox_add_character":
            return await _handle_add_character(arguments)
        elif name == "sandbox_get_state":
            return await _handle_get_state(arguments)
        elif name == "sandbox_write_scene":
            return await _handle_write_scene(arguments)
        elif name == "sandbox_compile_chapter":
            return await _handle_compile_chapter(arguments)
        elif name == "sandbox_update_graph":
            return await _handle_update_graph(arguments)
        elif name == "sandbox_check_consistency":
            return await _handle_check_consistency(arguments)
        elif name == "sandbox_export":
            return await _handle_export(arguments)
        elif name == "sandbox_set_budget":
            return await _handle_set_budget(arguments)
        elif name == "sandbox_get_budget":
            return await _handle_get_budget(arguments)
        else:
            return _err(f"Unknown tool: {name}")
    except Exception as e:
        return _err(f"Tool {name} failed: {str(e)}")


# ---------------------------------------------------------------------------
# Init
# ---------------------------------------------------------------------------

async def _handle_init(args: dict) -> list[TextContent]:
    vault = Path(args["vault_path"])
    world = args["world"]
    target = args.get("target_chapters", 30)
    genre = args.get("genre", "custom")

    writer = ObsidianWriter(vault)
    writer.create_vault_structure()

    # Apply genre preset defaults if genre is not custom
    if genre != "custom":
        preset = load_genre_template(genre)
        if preset:
            for key, default_val in preset.get("world_defaults", {}).items():
                world.setdefault(key, default_val)

    # Write world overview
    writer.write_world_overview(world)

    # Write core rule and conflict docs
    writer.write_world_doc("核心规则", "world_rule", world["core_rule"])
    writer.write_world_doc("核心冲突", "world_conflict", world["core_conflict"])

    # Initialize state
    state = SandboxState(vault)
    state.init(world, target)
    if genre != "custom":
        state.metadata["genre"] = genre
    state.save()

    # Write graph config
    writer.write_graph_config()

    # Write dashboard
    writer.write_dashboard()

    return _ok(f"Sandbox initialized at {vault}", {
        "target_chapters": target,
        "genre": genre,
        "world": world,
    })


# ---------------------------------------------------------------------------
# Add character
# ---------------------------------------------------------------------------

async def _handle_add_character(args: dict) -> list[TextContent]:
    vault = Path(args["vault_path"])
    state = SandboxState(vault)
    writer = ObsidianWriter(vault)

    name = args["name"]
    gender = args["gender"]
    personality = args["personality"]
    background = args["background"]
    motive = args["motive"]
    secret = args["secret"]
    rels = args.get("initial_relationships", {})

    # Write character file
    writer.write_character(name, gender, personality, background, motive, secret, rels)

    # Update state
    state.add_character(name, gender, personality, background, motive, secret, rels)
    state.save()

    return _ok(f"Character '{name}' added", {"relationships": rels})


# ---------------------------------------------------------------------------
# Get state
# ---------------------------------------------------------------------------

async def _handle_get_state(args: dict) -> list[TextContent]:
    vault = Path(args["vault_path"])
    include_mem = args.get("include_memories", True)
    state = SandboxState(vault)
    summary = state.get_summary(include_memories=include_mem)
    return _ok("State retrieved", summary)


# ---------------------------------------------------------------------------
# Write scene
# ---------------------------------------------------------------------------

async def _handle_write_scene(args: dict) -> list[TextContent]:
    vault = Path(args["vault_path"])
    state = SandboxState(vault)
    writer = ObsidianWriter(vault)

    round_num = args["round"]
    title = args["title"]
    narrative = args["narrative"]
    characters = args["characters"]
    quality = args.get("quality")
    scene_type = args.get("scene_type")
    rel_changes = args.get("relationship_changes", [])

    # Write scene file
    scene_file = writer.write_scene(
        round=round_num,
        title=title,
        date=args.get("date", datetime.now().strftime("%Y-%m-%d")),
        location=args.get("location", ""),
        characters=characters,
        emotional_arc=args.get("emotional_arc", ""),
        narrative=narrative,
        key_events=args.get("key_events", []),
        relationship_changes=rel_changes,
        quality=quality,
        scene_type=scene_type,
        has_foreshadowing=bool(args.get("foreshadowing_add")),
    )

    # Update character files
    for change in rel_changes:
        state.update_relationship(change["from_char"], change["to_char"], change["delta"])

    # Update character moods and memories
    for char_name in characters:
        char = state.get_character(char_name)
        if char:
            char["lastActiveRound"] = round_num
            char["roundsSinceActive"] = 0

    # Update foreshadowing
    for fs in args.get("foreshadowing_add", []):
        state.add_foreshadowing(fs, round_num)
    for fs in args.get("foreshadowing_resolve", []):
        state.resolve_foreshadowing(fs)

    # Create new locations
    for loc in args.get("new_locations", []):
        writer.write_location(loc, round_num)

    # Update state
    state.current_round = round_num
    state.add_scene_history(round_num, title, characters, args.get("location", ""),
                            quality=quality, scene_type=scene_type)
    state.increment_inactivity()
    state.archive_old_memories(round_num)
    state.save()

    return _ok(f"Scene S{round_num:03d}-{title} written", {"file": scene_file, "round": round_num})


# ---------------------------------------------------------------------------
# Compile chapter
# ---------------------------------------------------------------------------

async def _handle_compile_chapter(args: dict) -> list[TextContent]:
    vault = Path(args["vault_path"])
    writer = ObsidianWriter(vault)

    ch_num = args["chapter_number"]
    ch_title = args["chapter_title"]
    scene_range = args["scene_range"]
    text = args["narrative_text"]

    # Write chapter file
    chapter_file = writer.write_chapter(ch_num, ch_title, scene_range, text)

    # Move scene files into chapter subfolder
    writer.move_scenes_to_chapter_folder(ch_num, scene_range["start"], scene_range["end"])

    return _ok(f"Chapter {ch_num} '{ch_title}' compiled", {"file": chapter_file, "scenes": f"S{scene_range['start']:03d}-S{scene_range['end']:03d}"})


# ---------------------------------------------------------------------------
# Update graph
# ---------------------------------------------------------------------------

async def _handle_update_graph(args: dict) -> list[TextContent]:
    vault = Path(args["vault_path"])
    writer = ObsidianWriter(vault)
    colors = args.get("character_colors", {})
    writer.update_canvas(colors)
    return _ok("Canvas updated")


# ---------------------------------------------------------------------------
# Check consistency
# ---------------------------------------------------------------------------

async def _handle_check_consistency(args: dict) -> list[TextContent]:
    vault = Path(args["vault_path"])
    state = SandboxState(vault)
    chapter_range = args.get("chapter_range")

    findings = state.check_consistency(chapter_range)
    return _ok(f"Consistency check complete: {len(findings)} findings", {"findings": findings})


# ---------------------------------------------------------------------------
# Export
# ---------------------------------------------------------------------------

async def _handle_export(args: dict) -> list[TextContent]:
    vault = Path(args["vault_path"])
    state = SandboxState(vault)
    writer = ObsidianWriter(vault)

    export_dir = writer.export_novel(state)
    return _ok(f"Novel exported to {export_dir}")


# ---------------------------------------------------------------------------
# Budget
# ---------------------------------------------------------------------------

async def _handle_set_budget(args: dict) -> list[TextContent]:
    vault = Path(args["vault_path"])
    state = SandboxState(vault)

    for key in ("target_words", "daily_quota", "deadline", "chapter_budget"):
        if key in args:
            state.metadata[key] = args[key]
    state.save()

    return _ok("Budget updated", {"budget": {
        k: state.metadata[k]
        for k in ("target_words", "daily_quota", "deadline", "chapter_budget")
        if k in state.metadata
    }})


async def _handle_get_budget(args: dict) -> list[TextContent]:
    vault = Path(args["vault_path"])
    state = SandboxState(vault)

    budget = {
        k: state.metadata[k]
        for k in ("target_words", "daily_quota", "deadline", "chapter_budget")
        if k in state.metadata
    }

    # Compute current word count from scene history
    total_words = 0
    for scene in state._data.get("sceneHistory", []):
        q = scene.get("quality") or {}
        wc = q.get("word_count", 0)
        if wc:
            total_words += wc

    progress = {
        "current_round": state.current_round,
        "total_words": total_words,
        "scenes_written": len(state._data.get("sceneHistory", [])),
    }

    if budget.get("target_words"):
        progress["percent"] = round(total_words / budget["target_words"] * 100, 1)
        progress["remaining_words"] = budget["target_words"] - total_words

    if budget.get("daily_quota") and budget.get("target_words"):
        remaining = budget["target_words"] - total_words
        if remaining > 0 and budget["daily_quota"] > 0:
            import math
            progress["estimated_days_left"] = math.ceil(remaining / budget["daily_quota"])

    return _ok("Budget retrieved", {"budget": budget, "progress": progress})


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    import asyncio
    asyncio.run(stdio_server(app))


if __name__ == "__main__":
    main()

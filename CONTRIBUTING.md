# Contributing to story-sandbox

Thanks for your interest in contributing!

## Development setup

```bash
git clone https://github.com/houyuhang/story-sandbox.git
cd story-sandbox
pip install -e ".[dev]"
```

## Running tests

```bash
pytest
```

## Project structure

```
src/story_sandbox/
├── server.py              # MCP server entry point (tool definitions + handlers)
├── utils/
│   ├── state.py           # Sandbox state management (sandbox-state.json)
│   ├── obsidian.py        # Obsidian vault file writer
│   └── templates.py       # Template loading
templates/                 # Obsidian file templates
examples/                  # Example vaults
```

## Adding a new tool

1. Define the tool in `server.py` `list_tools()`
2. Implement the handler in `server.py`
3. If it needs file I/O, add a method to `ObsidianWriter` or `SandboxState`
4. Add a test
5. Update README.md tools table

## Code style

- Python 3.10+ features (type hints, match, etc.)
- Keep functions under 50 lines
- Docstrings on all public methods
- No external dependencies beyond `mcp`

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

# Contributing to story-sandbox / 贡献指南

Thanks for your interest in contributing! / 感谢你的贡献兴趣！

## Development setup / 开发环境

```bash
git clone https://github.com/houyuhang/story-sandbox.git
cd story-sandbox
pip install -e ".[dev]"
```

## Running tests / 运行测试

```bash
pytest
```

## Project structure / 项目结构

```
src/story_sandbox/
├── server.py              # MCP server entry point / MCP 服务器入口
├── utils/
│   ├── state.py           # Sandbox state management / 沙盒状态管理
│   ├── obsidian.py        # Obsidian vault file writer / Obsidian 文件写入
│   └── templates.py       # Template loading / 模板加载
templates/                 # Obsidian file templates / 模板文件
examples/                  # Example vaults / 示例 vault
```

## Adding a new tool / 添加新工具

1. Define the tool in `server.py` `list_tools()` / 在 `server.py` 中定义工具
2. Implement the handler / 实现处理函数
3. If it needs file I/O, add to `ObsidianWriter` or `SandboxState` / 需要文件操作时添加到对应工具类
4. Add a test / 添加测试
5. Update README.md tools table / 更新 README 工具表

## Code style / 代码风格

- Python 3.10+ features (type hints, match, etc.)
- Keep functions under 50 lines / 函数不超过 50 行
- Docstrings on all public methods / 所有公开方法需要文档字符串
- No external dependencies beyond `mcp` / 除 `mcp` 外不添加外部依赖

## License / 许可证

By contributing, you agree that your contributions will be licensed under the MIT License.

贡献即表示你同意你的贡献在 MIT 许可证下发布。

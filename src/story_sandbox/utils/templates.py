"""Template loading utilities."""
from pathlib import Path

TEMPLATE_DIR = Path(__file__).parent.parent.parent.parent / "templates"

def load_template(name: str) -> str:
    """Load a template file by name."""
    path = TEMPLATE_DIR / name
    if path.exists():
        return path.read_text(encoding="utf-8")
    return ""

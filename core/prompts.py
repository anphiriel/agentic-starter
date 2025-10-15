from pathlib import Path

def load_text(path: str) -> str:
    p = Path(path)
    return p.read_text(encoding="utf-8").strip()
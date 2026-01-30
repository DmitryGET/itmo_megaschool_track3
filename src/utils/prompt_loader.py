# Загрузка промптов (prompts/<role>.md)
from pathlib import Path
import src.config as config

def load_prompt(role: str) -> str:
    path = Path(config.PROMPTS_DIR) / f"{role}.md"
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")

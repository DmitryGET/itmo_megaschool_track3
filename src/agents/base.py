# src/agents/base.py
import os
import logging
from pathlib import Path
from src.llm import get_llm

logger = logging.getLogger(__name__)

class BaseAgent:
    def __init__(self, role: str):
        self.role = role
        self.llm = get_llm()
        
        # --- НАДЁЖНАЯ ЗАГРУЗКА ПРОМПТА ---
        # Ищем папку 'prompts' относительно расположения ЭТОГО ФАЙЛА (base.py)
        base_dir = Path(__file__).parent.parent  # src/agents/ -> src/
        project_root = base_dir.parent            # src/ -> корень проекта
        
        # Варианты расположения папки prompts
        prompt_dirs = [
            project_root / "prompts",      # корень проекта / prompts /
            base_dir / "prompts",          # src / prompts /
            Path.cwd() / "prompts"         # текущая рабочая директория / prompts /
        ]
        
        self.system_prompt = ""
        for prompt_dir in prompt_dirs:
            prompt_path = prompt_dir / f"{role}.md"
            if prompt_path.exists():
                try:
                    self.system_prompt = prompt_path.read_text(encoding="utf-8").strip()
                    logger.info(f"[BaseAgent] Загружен промпт '{role}' из: {prompt_path}")
                    break
                except Exception as e:
                    logger.warning(f"[BaseAgent] Ошибка чтения {prompt_path}: {e}")
        
        # КРИТИЧЕСКАЯ ПРОВЕРКА
        if not self.system_prompt:
            error_msg = (
                f"\n❌ КРИТИЧЕСКАЯ ОШИБКА: Не найден промпт для агента '{role}'!\n"
                f"Проверьте наличие файла:\n"
                f"  - prompts/{role}.md\n"
                f"Возможные пути поиска:\n" +
                "\n".join([f"  - {d}" for d in prompt_dirs])
            )
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)

    def _call_llm(self, user_content: str, max_tokens: int = 800) -> str:
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_content}
        ]
        resp = self.llm.chat_complete(messages, max_tokens=max_tokens)
        return resp.get("text", "").strip()
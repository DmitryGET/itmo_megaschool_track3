# Универсальный адаптер к Mistral (mistralai). Централизуем вызовы LLM.
from dataclasses import dataclass
from typing import List, Dict, Any
import logging
import os

from mistralai import Mistral  # убедитесь, что пакет установлен

import src.config as config

logger = logging.getLogger(__name__)

@dataclass
class LLMClient:
    api_key: str = config.MISTRAL_API_KEY
    model: str = config.MISTRAL_MODEL

    def __post_init__(self):
        if not self.api_key:
            raise RuntimeError("MISTRAL_API_KEY не задан в окружении")
        self.client = Mistral(api_key=self.api_key)

    def chat_complete(self, messages: List[Dict[str, str]], max_tokens: int = 1024) -> Dict[str, Any]:
        """
        messages: [{"role":"system"/"user"/"assistant","content":"..."}]
        Возвращает dict с полями text (строка) и raw (оригинал).
        """
        try:
            # В зависимости от версии библиотеки методы могут отличаться
            response = self.client.chat.complete(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens, 
                temperature=0.7,
                top_p=0.9
            )
            # Извлекаем текст в удобном виде; адаптируйте под конкретную версию клиента
            text = ""
            if hasattr(response, "choices") and response.choices:
                # Обычно response.choices[0].message.content
                choice = response.choices[0]
                if hasattr(choice, "message") and hasattr(choice.message, "content"):
                    text = choice.message.content
                elif hasattr(choice, "text"):
                    text = choice.text
            else:
                text = str(response)
            return {"text": text, "raw": response}
        except Exception as e:
            logger.exception("Ошибка LLM вызова")
            return {"text": "", "raw": None, "error": str(e)}

# Синглтон
_client = None

def get_llm() -> LLMClient:
    global _client
    if _client is None:
        _client = LLMClient()
    return _client

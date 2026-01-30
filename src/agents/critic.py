# CriticAgent — извлекает утверждения и выполняет факт-чекинг (через tools.fact_checker)
from typing import Dict, Any, List
from src.agents.base import BaseAgent
from src.tools.fact_checker import fact_check_claims


class CriticAgent(BaseAgent):
    def __init__(self):
        super().__init__(role="critic")  # prompts/critic.md

    def run(self, state, user_answer: str) -> Dict[str, Any]:
        # Генерация ответа с мыслями и утверждениями
        user_prompt = f"Ответ кандидата:\n{user_answer}\n\nПроанализируй и выдай вывод в формате с тегами [THOUGHT] и [CLAIMS]."
        raw = self._call_llm(user_prompt)
        
        # --- ИЗВЛЕЧЕНИЕ НАТИВНЫХ МЫСЛЕЙ ---
        critic_thought = ""
        try:
            if "[THOUGHT]" in raw and "[/THOUGHT]" in raw:
                critic_thought = raw.split("[THOUGHT]")[1].split("[/THOUGHT]")[0].strip()
        except Exception:
            pass
        
        # Сохраняем мысли в скрытый лог (только если есть)
        if critic_thought:
            state.hidden_observations.append(f"[Critic]: {critic_thought}\n")
        
        # --- ИЗВЛЕЧЕНИЕ УТВЕРЖДЕНИЙ ---
        claims = []
        try:
            if "[CLAIMS]" in raw and "[/CLAIMS]" in raw:
                claims_part = raw.split("[CLAIMS]")[1].split("[/CLAIMS]")[0].strip()
                import json
                parsed_claims = json.loads(claims_part)
                if isinstance(parsed_claims, list):
                    claims = [c for c in parsed_claims if isinstance(c, str)]
        except Exception:
            # ХАРДКОД ТОЛЬКО ЗДЕСЬ — фолбэк при ошибке парсинга
            claims = []
        
        # --- ФАКТ-ЧЕКИНГ (инструмент, не мысль агента) ---
        checks_result = fact_check_claims(claims)
        
        # Добавляем результат факт-чекинга как ОТДЕЛЬНУЮ запись в лог (не смешивая с мыслями)
        factcheck_summary = f"[Critic-FactCheck]: проверено {len(checks_result['checks'])} утверждений, итог={checks_result.get('overall_flag', 'ok')}\n"
        state.hidden_observations.append(factcheck_summary)
        
        return {
            "checks": checks_result["checks"],
            "overall_flag": checks_result["overall_flag"],
            "claims_extracted": claims
        }
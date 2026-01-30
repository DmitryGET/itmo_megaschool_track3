# FeedbackAgent — генерация финального фидбэка через LLM в формате markdown
from typing import Dict, Any
from src.agents.base import BaseAgent

class FeedbackAgent(BaseAgent):
    def __init__(self):
        super().__init__(role="feedback")  # prompts/feedback.md

    def run(self, state) -> str:
        # Собираем полную историю интервью для контекста
        history_lines = []
        for turn in getattr(state, 'turns', []):
            history_lines.append(f"Вопрос: {turn.agent_visible_message}")
            history_lines.append(f"Ответ: {turn.user_message}")
            history_lines.append(f"Мысли: {turn.internal_thoughts}")
            history_lines.append("---")
        
        # Собираем скрытые наблюдения (если есть отдельно от turns)
        hidden_obs = getattr(state, 'hidden_observations', [])
        hidden_str = "\n".join(hidden_obs[-20:]) if hidden_obs else "Нет дополнительных наблюдений"
        
        # Собираем оценку скиллов (если есть)
        skill_estimate = getattr(state, 'skill_estimate', {})
        skill_str = ", ".join([f"{k}: {v:.2f}" for k, v in skill_estimate.items()]) if skill_estimate else "Не оценено"
        histtory_interview = '\n'.join(history_lines[:50])
        user_prompt = (
            f"Полная история интервью:\n{histtory_interview}\n\n"  # Ограничиваем длину
            f"Дополнительные наблюдения агентов:\n{hidden_str}\n\n"
            f"Оценка скиллов (если доступна):\n{skill_str}\n\n"
            "Сгенерируй финальный фидбэк строго по структуре из системного промпта. "
            "Выводи ТОЛЬКО текст фидбэка в формате Markdown (без обёрток ```markdown```)."
        )
        
        raw_feedback = self._call_llm(user_prompt).strip()
        
        # Сохраняем фидбэк как строку в состоянии
        state.final_feedback = raw_feedback
        
        return raw_feedback
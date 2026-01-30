# MentorAgent — скрытая рефлексия. Формирует internal_note и instruction_for_reviewer.
from typing import Dict, Any
from src.agents.base import BaseAgent

class MentorAgent(BaseAgent):
    def __init__(self):
        super().__init__(role="mentor")  # prompts/mentor.md

    def run(self, state, user_answer: str, critic_report: Dict[str, Any]) -> Dict[str, Any]:
        critic_flag = critic_report.get("overall_flag", "no_issues")
        dialogue_snippet = "\n".join(state.dialogue_history[-10:]) if hasattr(state, 'dialogue_history') else ""
        
        user_prompt = (
            f"Ответ кандидата:\n{user_answer}\n\n"
            f"Отчёт Критика (флаг): {critic_flag}\n\n"
            f"История диалога (последние 10 строк):\n{dialogue_snippet}\n\n"
            "Проанализируй ответ и сформируй вывод в требуемом формате с тегами [THOUGHT] и [JSON]."
        )
        
        raw = self._call_llm(user_prompt)
        
        # --- ИЗВЛЕЧЕНИЕ НАТИВНЫХ МЫСЛЕЙ ИЗ [THOUGHT] ---
        mentor_thought = ""
        try:
            if "[THOUGHT]" in raw and "[/THOUGHT]" in raw:
                mentor_thought = raw.split("[THOUGHT]")[1].split("[/THOUGHT]")[0].strip()
        except Exception:
            pass
        
        # Сохраняем мысли в скрытый лог (только если они есть)
        if mentor_thought:
            state.hidden_observations.append(f"[Mentor]: {mentor_thought}\n")
        
        # --- ПАРСИНГ JSON (только из [JSON] тега) ---
        try:
            json_part = raw.split("[JSON]")[1].split("[/JSON]")[0].strip()
            import json
            parsed_data = json.loads(json_part)
            internal_note = parsed_data.get("internal_note", "")
            instruction = parsed_data.get("instruction_for_reviewer", "ask_clarify")
            severity = parsed_data.get("severity", "medium")
            confidence = float(parsed_data.get("confidence_assessment", 0.6))
        except Exception:
            # ХАРДКОД ТОЛЬКО ЗДЕСЬ — как фолбэк при ошибке
            internal_note = f"Ошибка парсинга. Флаг критика: {critic_flag}"
            instruction = "ask_clarify"
            severity = "medium"
            confidence = 0.6
        
        return {
            "internal_note": internal_note,
            "instruction_for_reviewer": instruction,
            "severity": severity,
            "confidence_assessment": confidence
        }
# ManagerAgent — агрегирует сигналы и принимает решение через LLM (не rule-based)
from typing import Dict, Any
from src.agents.base import BaseAgent

class ManagerAgent(BaseAgent):
    def __init__(self):
        super().__init__(role="manager")  # prompts/manager.md

    def run(self, state, mentor_signal: Dict[str, Any], critic_report: Dict[str, Any]) -> Dict[str, Any]:
        # Подготовка контекста для LLM
        mentor_note = mentor_signal.get("internal_note", "нет анализа")
        mentor_severity = mentor_signal.get("severity", "medium")
        mentor_instruction = mentor_signal.get("instruction_for_reviewer", "continue")
        
        critic_flag = critic_report.get("overall_flag", "no_issues")
        critic_checks_count = len(critic_report.get("checks", []))
        
        # Прогресс интервью
        question_count = len([m for m in getattr(state, 'dialogue_history', []) if m.startswith("Agent:")])
        max_questions = getattr(state, 'max_questions', 10)
        skill_estimate = getattr(state, 'skill_estimate', {})
        avg_skill = sum(skill_estimate.values()) / len(skill_estimate) if skill_estimate else 0.5
        
        user_prompt = (
            f"Сигнал Ментора:\n"
            f"  Анализ: {mentor_note}\n"
            f"  Severity: {mentor_severity}\n"
            f"  Рекомендация: {mentor_instruction}\n\n"
            f"Отчёт Критика:\n"
            f"  Overall flag: {critic_flag}\n"
            f"  Проверено утверждений: {critic_checks_count}\n\n"
            f"Прогресс интервью:\n"
            f"  Задано вопросов: {question_count} из {max_questions}\n"
            f"  Средняя оценка скиллов: {avg_skill:.2f}\n\n"
            f"Прими решение о дальнейшем ходе интервью и выдай вывод в формате с тегами [THOUGHT] и [JSON]."
        )
        
        raw = self._call_llm(user_prompt)
        
        # --- ИЗВЛЕЧЕНИЕ НАТИВНЫХ МЫСЛЕЙ ---
        manager_thought = ""
        try:
            if "[THOUGHT]" in raw and "[/THOUGHT]" in raw:
                manager_thought = raw.split("[THOUGHT]")[1].split("[/THOUGHT]")[0].strip()
        except Exception:
            pass
        
        # Сохраняем мысли в скрытый лог
        if manager_thought:
            state.hidden_observations.append(f"[Manager]: {manager_thought}\n")
        
        # --- ПАРСИНГ РЕШЕНИЯ ИЗ JSON ---
        try:
            json_part = raw.split("[JSON]")[1].split("[/JSON]")[0].strip()
            import json
            parsed = json.loads(json_part)
            decision = parsed.get("decision", "continue")
            instruction = parsed.get("instruction_for_reviewer", mentor_instruction)
            reason = parsed.get("reason", "решение принято на основе анализа")
            confidence = float(parsed.get("confidence", 0.7))
        except Exception:
            # ХАРДКОД ТОЛЬКО ЗДЕСЬ — фолбэк при ошибке
            decision = "continue"
            instruction = mentor_instruction
            reason = f"Ошибка парсинга. Флаг критика: {critic_flag}, severity: {mentor_severity}"
            confidence = 0.6
        
        return {
            "decision": decision,
            "instruction_for_reviewer": instruction,
            "decision_reason": reason,
            "confidence": confidence
        }
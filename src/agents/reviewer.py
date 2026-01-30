from typing import Dict, Any, Optional
from src.agents.base import BaseAgent
import src.config as config
from src.utils.intent_classifier import classify_question


class ReviewerAgent(BaseAgent):
    def __init__(self):
        super().__init__(role="reviewer")  # prompts/reviewer.md

    def run(self, state, internal_thoughts: str = "", topic_hint: Optional[str] = None) -> Dict[str, Any]:
        """
        Возвращает:
        {
          "visible_message": "...",
          "metadata": {"topic": "...", "difficulty": "...", "intent": "..."}
        }
        """
        # --- 1. Подготовка входных данных согласно новому промпту ---
        
        candidate_name = getattr(state.candidate, 'name', "Кандидат") or "Кандидат"
        position = getattr(state.candidate, 'position', "Backend Developer") or "Backend Developer"
        grade = getattr(state.candidate, 'grade', "Junior") or "Junior"
        experience_years = getattr(state.candidate, 'experience_years', 0) or 0
        
        # --- Формирование контекста профиля ---
        profile_context = (
            f"ИМЯ: {candidate_name}\n"
            f"ПОЗИЦИЯ: {position}\n"
            f"ГРЕЙД: {grade}\n"
            f"ОПЫТ: {experience_years} лет"
        )
        
        # --- История диалога ---
        st_hist = "\n".join(state.dialogue_history[-config.REVIEWER_ST_MEMORY*2:]) if state.dialogue_history else "Диалог только начался"
        
        # --- ФОРМИРОВАНИЕ ПРОМПТА ---
        user_prompt = (
            f"=== ПРОФИЛЬ КАНДИДАТА ===\n{profile_context}\n\n"
            
            f"=== КЛЮЧЕВОЕ ПРАВИЛО ===\n"
            f"ЗАДАВАЙ ВОПРОСЫ ТОЛЬКО ПО ТЕХНОЛОГИЯМ, УКАЗАННЫМ В ПОЗИЦИИ '{position}'.\n"
            f"НЕ спрашивай про технологии, не относящиеся к этой позиции.\n\n"
            
            f"=== ИСТОРИЯ ДИАЛОГА ===\n{st_hist}\n\n"
            
            f"=== АНАЛИЗ АГЕНТОВ ===\n{internal_thoughts}\n\n"
            
            f"=== ЗАДАЧА ===\n"
            f"1. Обратись к кандидату ПО ИМЕНИ: '{candidate_name}, ...'\n"
            f"2. Задай ОДИН конкретный технический вопрос по технологиям из позиции '{position}'.\n"
            f"3. Для грейда '{grade}' адаптируй сложность (Junior → базовые концепции).\n"
            f"4. НЕ задавай общие вопросы 'расскажите о проекте'.\n\n"
            
            f"=== ФОРМАТ ВЫВОДА ===\n"
            f"{candidate_name}, <конкретный технический вопрос>\n\n"
            f"[THOUGHT]\n<обоснование выбора технологии и сложности>\n[/THOUGHT]\n"
            f"METADATA: {{\"topic\":\"...\",\"difficulty\":\"{grade.lower()}\",\"intent\":\"probe\"}}"
        )

        # --- 2. Вызов LLM ---
        raw = self._call_llm(user_prompt)
        visible = raw.strip()
        metadata = {
            "topic": topic_hint or "general", 
            "difficulty": getattr(state, 'current_difficulty', 'medium'), 
            "intent": "probe"
        }
        
        # --- 3. Парсинг ответа ---
        visible = raw.strip()
        reviewer_thought = ""
        visible = visible.split("[THOUGHT]")[0].strip()
        
        if "[THOUGHT]" in raw and "[/THOUGHT]" in raw:
            try:
                # Видимое сообщение — всё до [THOUGHT]
                visible = visible.split("[THOUGHT]")[0].strip()
                # Мысли — между тегами
                reviewer_thought = raw.split("[THOUGHT]")[1].split("[/THOUGHT]")[0].strip()
            except Exception:
                pass  # fallback: весь ответ как видимое сообщение
        
        # --- Сохраняем мысли в формате ТЗ: "[Reviewer]: ...\n" ---
        if reviewer_thought:
            state.hidden_observations.append(f"[Reviewer]: {reviewer_thought}\n")
        if "\nMETADATA:" in raw:
            parts = raw.split("\nMETADATA:", 1) # Разделяем только по первому вхождению
            visible = parts[0].strip()
            try:
                import json
                metadata = json.loads(parts[1].strip())
            except Exception:
                pass # Оставляем метаданные по умолчанию
        
        # --- 4. Классификация вопроса ---
        is_technical, rationale = classify_question(visible)
        
        return {
            "visible_message": visible, 
            "metadata": metadata, 
            "is_technical": is_technical, 
            "rationale": rationale
        }

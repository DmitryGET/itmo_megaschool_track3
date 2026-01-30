# Парсер неструктурированного описания кандидата
# Простая эвристика + точка интеграции с LLM, если нужен более точный парсинг.
import re
from typing import Dict, Any
from src.llm import get_llm


def extract_name_from_text(text: str) -> str | None:
    """
    Извлекает ФИО из свободного текста с помощью эвристик.
    Поддерживает: Имя, Имя+Фамилия, Имя+Отчество, Полное ФИО (рус/англ).
    """
    text = text.strip()
    text_lower = text.lower()
    
    # --- Эвристика 1: поиск после ключевых фраз ---
    patterns = [
        r'(?:меня\s+зовут|зовут|имя|я\s+зовут|зовут\s+меня|я)\s+([А-ЯЁA-Z][а-яёa-z]+(?:\s+[А-ЯЁA-Z][а-яёa-z]+(?:\s+[А-ЯЁA-Z][а-яёa-z]+)?)?)',
        r'^я\s+([А-ЯЁA-Z][а-яёa-z]+(?:\s+[А-ЯЁA-Z][а-яёa-z]+(?:\s+[А-ЯЁA-Z][а-яёa-z]+)?)?)',
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            name_candidate = match.group(1).strip()
            # Валидация: минимум 2 буквы, не приветствие
            if len(name_candidate) >= 2 and not is_greeting(name_candidate):
                return name_candidate
    
    # --- Эвристика 2: анализ первых слов с заглавной буквы ---
    # Ищем все слова с заглавной буквы в начале текста (до первой точки или запятой)
    first_sentence = re.split(r'[.,!?]', text)[0]
    words = re.findall(r'\b([А-ЯЁA-Z][а-яёa-z]+)\b', first_sentence)
    
    # Фильтруем приветствия и гео-названия
    filtered = [w for w in words if len(w) >= 2 and not is_greeting(w.lower()) and not is_location(w.lower())]
    
    if filtered:
        # Берём первые 1-3 слова (ФИО обычно не длиннее 3 слов)
        name_parts = filtered[:3]
        return " ".join(name_parts)
    
    return None

def is_greeting(word: str) -> bool:
    """Проверяет, является ли слово приветствием."""
    greetings = {
        "привет", "здравствуйте", "добрый", "доброе", "доброе", "хай", "хеллоу", "прив",
        "здрасти", "йоу", "приветствую", "здравствуй", "доброго", "добрый"
    }
    return word.lower() in greetings

def is_location(word: str) -> bool:
    """Проверяет, является ли слово географическим названием (упрощённо)."""
    # Базовый список для фильтрации (можно расширить)
    locations = {
        "москва", "питер", "петербург", "санкт", "новосибирск", "екатеринбург",
        "казань", "самара", "омск", "россия", "москве", "питере"
    }
    return word.lower() in locations


def parse_free_text_profile(text: str, use_llm: bool = False) -> Dict[str, Any]:
    """
    Преобразует неструктурированный текст в структуру CandidateProfile.
    Если use_llm=True — используем LLM для более точного парсинга.
    """
    if use_llm:
        # Используем промпт parser (можно создать prompts/parser.md)
        system = "Вы — помощник. Извлеките данные о кандидате в JSON."
        user = f"Текст профиля кандидата:\n{text}\n\nВерните JSON: {{'name':..., 'position':..., 'grade':..., 'experience_years': number, 'behavior': [..]}}"
        resp = get_llm().chat_complete([{"role":"system","content":system},{"role":"user","content":user}])
        try:
            import json
            j = json.loads(resp["text"])
            return j
        except Exception:
            # падение — fallback на эвристику ниже
            pass

    # Простая эвристическая экстракция
    result = {"name": None, "position": None, "grade": None, "experience_years": None, "behavior": []}
    result["name"] = extract_name_from_text(text)

    exp_match = re.search(r"(\d+)\s*(?:год|лет|года)", text)
    if exp_match:
        result["experience_years"] = float(exp_match.group(1))

    # grade heuristics
    low = text.lower()
    if "senior" in low or "сеньор" in low or "senior" in text:
        result["grade"] = "Senior"
    elif "middle" in low or "middle" in text or "мидл" in low:
        result["grade"] = "Middle"
    elif "junior" in low or "джун" in low or "junior" in text:
        result["grade"] = "Junior"

    # position heuristics
    if "backend" in low or "бэкенд" in low:
        result["position"] = "Backend Developer"
    elif "data" in low or "ml" in low or "ml engineer" in low:
        result["position"] = "ML Engineer"

    return result

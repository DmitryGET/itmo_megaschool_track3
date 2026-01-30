# Простой классификатор: технический ли вопрос (counts toward 10) или служебный/вакансии/HR (не считается)
# Здесь можно использовать LLM или правило-ограничитель. Для начала — гибрид эвристик.

from typing import Tuple
import re

TECH_KEYWORDS = [
    "алгоритм", "структур", "оптимиз", "сложность", "big o",
    "процесс", "модель", "api", "sql", "бд", "python", "java", "c++", "система", "design", "архитектур"
]

NONTECH_KEYWORDS = [
    "зарплат", "офис", "местополож", "отпуск", "график", "бенефит", "ваканси", "котируется", "контракт", "услов", "как устроено в компании"
]

def classify_question(text: str) -> Tuple[bool, str]:
    """
    Возвращает (is_technical, rationale)
    is_technical=True - считается техническим вопросом и входит в лимит MAX_TECHNICAL_QUESTIONS
    """
    low = text.lower()
    # явные non-tech
    for k in NONTECH_KEYWORDS:
        if k in low:
            return False, "detected_nontech_keyword"
    # явная техника
    for k in TECH_KEYWORDS:
        if k in low:
            return True, "detected_tech_keyword"
    # fallback: если вопрос содержит 'что такое', 'как работает', 'объясни' — технический
    if re.search(r"что такое|как работает|объясни|приведи пример|как бы вы", low):
        return True, "fallback_pattern"
    # иначе считаем non-tech
    return False, "default_nontech"

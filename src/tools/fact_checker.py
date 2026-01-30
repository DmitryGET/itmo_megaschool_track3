# Интерфейс факт-чекинга. Возвращает структуру checks согласно промпту critic.md
from typing import List, Dict, Any
import src.config as config

def fact_check_claims(claims: List[str]) -> Dict[str, Any]:
    """
    Заглушка: локальная проверка. При RAG_ENABLED надо подключить retriever и собрать evidence.
    Возвращает структуру:
    {
      "checks": [{"claim":..., "verdict":"true|false|unknown|contradictory", "confidence":0..1, "evidence":[...], "explanation": "..."}],
      "overall_flag": "no_issues|minor_issues|major_issues|contradictory"
    }
    """
    checks = []
    for c in claims:
        low = c.lower()
        if "gil" in low or "g i l" in low:
            checks.append({
                "claim": c,
                "verdict": "false",
                "confidence": 0.95,
                "evidence": [{"title":"CPython docs","source":"docs.python.org","snippet":"GIL exists in CPython"}],
                "explanation": "GIL не удален в CPython"
            })
        else:
            checks.append({
                "claim": c,
                "verdict": "unknown",
                "confidence": 0.2,
                "evidence": [],
                "explanation": "нет локальных данных"
            })
    overall = "no_issues"
    if any(ch["verdict"] == "false" for ch in checks):
        overall = "major_issues"
    return {"checks": checks, "overall_flag": overall}

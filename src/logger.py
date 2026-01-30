# Сериализация интервью в interview_log.json по строго заданному формату
import json
from pathlib import Path
import src.config as config
from typing import Any, Dict

LOG_DIR = Path(config.LOGS_DIR)
LOG_DIR.mkdir(parents=True, exist_ok=True)

def save_interview_log(state, filename: str = None) -> Path:
    """
    Сохраняет state в JSON в required format:
    {
      "participant_name": "...",
      "turns": [ {turn_id, agent_visible_message, user_message, internal_thoughts} ... ],
      "final_feedback": { ... }
    }
    """
    if filename is None:
        participant = state.candidate.name or "unknown"
        filename = f"interview_{participant.replace(' ','_')}.json"
    out = {
        "participant_name": state.candidate.name or "",
        "turns": [],
        "final_feedback": None
    }
    for t in state.turns:
        out["turns"].append({
            "turn_id": t.turn_id,
            "agent_visible_message": t.agent_visible_message,
            "user_message": t.user_message,
            "internal_thoughts": t.internal_thoughts
        })
    if state.final_feedback:
        out["final_feedback"] = state.final_feedback
    path = LOG_DIR / filename
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    return path

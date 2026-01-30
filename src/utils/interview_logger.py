import json
from typing import List, Dict
from config import LOG_PATH


class InterviewLogger:
    def __init__(self, participant_name: str):
        self.log = {
            "participant_name": participant_name,
            "turns": [],
            "final_feedback": None
        }
        self.turn_id = 1

    def add_turn(self, user_message: str, internal_thoughts: str, agent_message: str):
        self.log["turns"].append({
            "turn_id": self.turn_id,
            "user_message": user_message,
            "internal_thoughts": internal_thoughts,
            "agent_visible_message": agent_message
        })
        self.turn_id += 1

    def add_final_feedback(self, feedback: str):
        self.log["final_feedback"] = feedback

    def save(self):
        with open(LOG_PATH, "w", encoding="utf-8") as f:
            json.dump(self.log, f, ensure_ascii=False, indent=2)

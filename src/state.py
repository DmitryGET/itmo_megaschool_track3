# Подробная модель состояния интервью — единый источник правды.
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field

class Turn(BaseModel):
    turn_id: int
    agent_visible_message: str
    user_message: str
    internal_thoughts: str  # агрегат Mentor/Critic/Manager заметок для этого turn
    technical_question: bool = True  # отмечаем: считается ли это technical вопрос (по правилам)

class CandidateProfile(BaseModel):
    name: Optional[str] = None
    position: Optional[str] = None
    grade: Optional[str] = None
    experience_years: Optional[float] = None
    behavior: List[str] = Field(default_factory=list)  # поведенческие указания из таблицы/файла

class FinalFeedback(BaseModel):
    verdict: Dict[str, Any]
    technical_review: List[Dict[str, Any]]
    soft_skills: Dict[str, Any]
    personal_roadmap: List[Dict[str, Any]]
    raw_metrics: Dict[str, int]
    final_notes: str

class InterviewState(BaseModel):
    # Профиль кандидата (структур/неструктурный парсер должен заполнить)
    candidate: CandidateProfile = Field(default_factory=CandidateProfile)

    # Журнал turn'ов
    turns: List[Turn] = Field(default_factory=list)
    current_turn_id: int = 0

    # Логика подсчёта: считаем только technical_question == True
    technical_questions_asked: int = 0

    # Диалог для short-term memory (строки вида "Agent: ...", "User: ...")
    dialogue_history: List[str] = Field(default_factory=list)

    # Скрытые заметки от агентов (Mentor/Critic/Manager)
    hidden_observations: List[str] = Field(default_factory=list)

    # Оценки скиллов (topic -> score 0..1)
    skill_estimate: Dict[str, float] = Field(default_factory=dict)

    # Флаги и признаки
    decision_flags: Dict[str, Any] = Field(default_factory=dict)

    # Итоговый фидбек
    final_feedback: Optional[str] = None 

    def append_turn(self, agent_message: str, user_message: str, internal_thoughts: str, technical_question: bool = True):
        """
        Добавление turn в state. Нумерация начинается с 1.
        При technical_question=True увеличиваем счётчик технических вопросов.
        """
        self.current_turn_id += 1
        if technical_question:
            self.technical_questions_asked += 1
        t = Turn(
            turn_id=self.current_turn_id,
            agent_visible_message=agent_message,
            user_message=user_message,
            internal_thoughts=internal_thoughts,
            technical_question=technical_question
        )
        self.turns.append(t)
        self.dialogue_history.append(f"Agent: {agent_message}")
        self.dialogue_history.append(f"User: {user_message}")

# main.py

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.state import InterviewState, CandidateProfile
from src.router import run_interview_loop

def main():
    print("=== Multiagent Technical Interviewer ===\n")
    
    name = input("Имя: ").strip()
    position = input("Позиция: ").strip()
    grade = input("Грейд: ").strip()
    experience_years = input("Опыт (лет): ").strip()
    
    state = InterviewState()
    state.candidate.name = name
    state.candidate.position = position
    state.candidate.grade = grade
    state.candidate.experience_years = experience_years
    
    print(f"\n✅ Профиль: {name}, {grade} {position}")
    
    # --- ХОД 1: первое сообщение кандидата ---
    print(f"\n[Interviewer]: Привет, {name}! Расскажите о себе и вашем опыте.")
    first_answer = input("[Вы]: ").strip()
    
    state.append_turn(
        agent_message=f"Привет, {name}! Расскажите о себе и вашем опыте.",
        user_message=first_answer,
        internal_thoughts="[System]: initial introduction\n",
        technical_question=False
    )
    
    print("\n--- НАЧАЛО ИНТЕРВЬЮ ---")
    run_interview_loop(state)

if __name__ == "__main__":
    main()
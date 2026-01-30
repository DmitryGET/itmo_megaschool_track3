# router.py

from src.agents.reviewer import ReviewerAgent
from src.agents.critic import CriticAgent
from src.agents.mentor import MentorAgent
from src.agents.manager import ManagerAgent
from src.agents.feedback import FeedbackAgent
import src.config as config
from src.logger import save_interview_log

def run_interview_loop(state, input_func=input, output_func=print):
    reviewer = ReviewerAgent()
    critic = CriticAgent()
    mentor = MentorAgent()
    manager = ManagerAgent()
    feedback_agent = FeedbackAgent()
    
    termination_phrases = ["стоп", "фидбэк", "остановить", "хватит", "стоп интервью", "stop", "end", "quit", "feedback"]
    
    while True:
        # Получаем вопрос от интервьюера
        previous_thoughts = "".join(state.hidden_observations)
        state.hidden_observations = []
        
        rev_out = reviewer.run(state, internal_thoughts=previous_thoughts)
        visible = rev_out["visible_message"]
        
        output_func(f"\n[Интервьюер]: {visible}")
        user_answer = input_func("[Вы]: ").strip()
        
        # Сохраняем ЛЮБОЙ ответ как ход (даже "стоп интервью")
        if any(p in user_answer.lower() for p in termination_phrases):
            state.append_turn(
                agent_message=visible,
                user_message=user_answer,
                internal_thoughts="[System]: interview stopped by user\n",
                technical_question=False
            )
            save_interview_log(state)
            break
        
        # Анализ агентами
        critic_report = critic.run(state, user_answer)
        mentor_signal = mentor.run(state, user_answer, critic_report)
        manager_decision = manager.run(state, mentor_signal, critic_report)
        
        # Сохраняем ход
        current_thoughts = "".join(state.hidden_observations)
        state.hidden_observations = []
        
        state.append_turn(
            agent_message=visible,
            user_message=user_answer,
            internal_thoughts=current_thoughts,
            technical_question=True
        )
        save_interview_log(state)
        
        # Проверка завершения
        if state.technical_questions_asked >= config.MAX_TECHNICAL_QUESTIONS:
            break
        if manager_decision.get("decision") == "end_interview":
            break
    
    # Фидбэк
    fb = feedback_agent.run(state)
    state.final_feedback = fb
    save_interview_log(state)
    
    output_func("\n--- ФИНАЛЬНЫЙ ФИДБЭК ---")
    output_func(fb)
    return state
# Конфигурация проекта (переменные окружения, константы)
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).resolve().parent

MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "")
MISTRAL_MODEL = os.getenv("MISTRAL_MODEL", "mistral-small-latest")

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "qwen/qwen3-32b")

# Путь к папке с промптами (файлы prompts/<role>.md)
PROMPTS_DIR = ROOT.parent / "prompts"

# Максимум технических вопросов от интервьюера (считается только technical turns)
MAX_TECHNICAL_QUESTIONS = int(os.getenv("MAX_TECH_QUESTIONS", "10"))

# Сколько последних turn-ов смотреть для short-term memory reviewer'а
REVIEWER_ST_MEMORY = int(os.getenv("REVIEWER_ST_MEMORY", "6"))

# Логи
LOGS_DIR = ROOT / "logs" / "interview_logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# RAG / Fact-check placeholders
RAG_ENABLED = os.getenv("RAG_ENABLED", "false").lower() == "true"
RAG_ENDPOINT = os.getenv("RAG_ENDPOINT", "")

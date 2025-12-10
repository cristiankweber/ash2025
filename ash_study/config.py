"""
config.py - Configurações da ASH-SAP Study Platform
"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Caminhos
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

# Arquivos de dados
COURSE_DATA_FILE = DATA_DIR / "course_structure.json"
PROGRESS_FILE = DATA_DIR / "user_progress.json"
LESSONS_FILE = DATA_DIR / "completed_lessons.json"

# API
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514")
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.3"))
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "4096"))

# Configurações pedagógicas
QUESTIONS_PER_LESSON = int(os.getenv("QUESTIONS_PER_LESSON", "5"))
PASSING_SCORE = float(os.getenv("PASSING_SCORE", "0.7"))  # 70%
REVIEW_INTERVAL_DAYS = int(os.getenv("REVIEW_INTERVAL_DAYS", "7"))


def validate_config() -> tuple[bool, list[str]]:
    """Valida configurações necessárias."""
    errors = []
    if not ANTHROPIC_API_KEY:
        errors.append("ANTHROPIC_API_KEY não configurada")
    return len(errors) == 0, errors

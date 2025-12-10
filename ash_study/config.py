"""
config.py - Configurações da ASH-SAP Study Platform (Modo Offline)
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

# Modo de operação
# "offline" = Apenas importa e navega lições existentes
# "online" = Gera novas lições via API (requer API key)
MODE = os.getenv("MODE", "offline")

# Configurações pedagógicas
PASSING_SCORE = float(os.getenv("PASSING_SCORE", "0.7"))  # 70%
REVIEW_INTERVAL_DAYS = int(os.getenv("REVIEW_INTERVAL_DAYS", "7"))


def validate_config() -> tuple[bool, list[str]]:
    """Valida configurações - sempre válido no modo offline."""
    return True, []


def is_offline_mode() -> bool:
    """Verifica se está em modo offline."""
    return MODE == "offline"

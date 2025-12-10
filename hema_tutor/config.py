"""
config.py - Configurações centralizadas do HemaTutor

Este módulo é responsável por:
- Carregar variáveis de ambiente do arquivo .env
- Definir configurações de modelo LLM (OpenAI GPT-4o ou Claude 3.5 Sonnet)
- Definir configurações de VectorStore (FAISS ou ChromaDB)
- Parâmetros de chunking e processamento de PDF
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from typing import Literal

# ============================================
# CARREGAMENTO DO .ENV
# ============================================
load_dotenv()

# ============================================
# CAMINHOS DO PROJETO
# ============================================
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
UPLOADS_DIR = DATA_DIR / "uploads"
VECTORSTORES_DIR = DATA_DIR / "vectorstores"

# Garantir que os diretórios existam
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
VECTORSTORES_DIR.mkdir(parents=True, exist_ok=True)

# ============================================
# CHAVES DE API
# ============================================
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

# ============================================
# CONFIGURAÇÃO DO MODELO LLM
# ============================================
# Opções: "openai" ou "anthropic"
LLM_PROVIDER: Literal["openai", "anthropic"] = os.getenv("LLM_PROVIDER", "openai")

# Modelos disponíveis
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")

# Temperatura do modelo (0.0 = determinístico, 1.0 = criativo)
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.3"))

# Máximo de tokens na resposta
LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "4096"))

# ============================================
# CONFIGURAÇÃO DO VECTORSTORE
# ============================================
# Opções: "faiss" ou "chroma"
VECTORSTORE_TYPE: Literal["faiss", "chroma"] = os.getenv("VECTORSTORE_TYPE", "faiss")

# Modelo de embeddings (OpenAI)
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")

# ============================================
# CONFIGURAÇÃO DE CHUNKING
# ============================================
# Tamanho do chunk em caracteres (aproximadamente 1000-1500 tokens)
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1200"))

# Overlap entre chunks para manter contexto
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "250"))

# ============================================
# CONFIGURAÇÃO DE RAG
# ============================================
# Número de chunks retornados na busca
RETRIEVER_K = int(os.getenv("RETRIEVER_K", "6"))

# Score mínimo de similaridade (0.0 a 1.0)
SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", "0.5"))

# ============================================
# TRILHAS DE APRENDIZADO (DEFAULT)
# ============================================
# Trilhas padrão caso o sistema não consiga extrair do PDF
DEFAULT_TRACKS = [
    "Anemias",
    "Hemostasia e Trombose",
    "Neoplasias Hematológicas",
    "Transplante de Medula Óssea",
    "Hemoglobinopatias",
    "Distúrbios Leucocitários",
    "Medicina Transfusional",
]

# ============================================
# CONFIGURAÇÃO DO QUIZ
# ============================================
# Número de questões por lição
QUESTIONS_PER_QUIZ = int(os.getenv("QUESTIONS_PER_QUIZ", "3"))

# Número de alternativas por questão
OPTIONS_PER_QUESTION = int(os.getenv("OPTIONS_PER_QUESTION", "4"))


def get_llm_config() -> dict:
    """
    Retorna a configuração do LLM baseada no provider selecionado.

    Returns:
        dict: Configuração contendo provider, model, api_key, temperature, max_tokens
    """
    if LLM_PROVIDER == "openai":
        return {
            "provider": "openai",
            "model": OPENAI_MODEL,
            "api_key": OPENAI_API_KEY,
            "temperature": LLM_TEMPERATURE,
            "max_tokens": LLM_MAX_TOKENS,
        }
    else:
        return {
            "provider": "anthropic",
            "model": ANTHROPIC_MODEL,
            "api_key": ANTHROPIC_API_KEY,
            "temperature": LLM_TEMPERATURE,
            "max_tokens": LLM_MAX_TOKENS,
        }


def get_vectorstore_config() -> dict:
    """
    Retorna a configuração do VectorStore.

    Returns:
        dict: Configuração contendo type, persist_directory, embedding_model
    """
    return {
        "type": VECTORSTORE_TYPE,
        "persist_directory": str(VECTORSTORES_DIR),
        "embedding_model": EMBEDDING_MODEL,
    }


def validate_config() -> tuple[bool, list[str]]:
    """
    Valida se as configurações necessárias estão definidas.

    Returns:
        tuple: (is_valid, list_of_errors)
    """
    errors = []

    if LLM_PROVIDER == "openai" and not OPENAI_API_KEY:
        errors.append("OPENAI_API_KEY não configurada no .env")

    if LLM_PROVIDER == "anthropic" and not ANTHROPIC_API_KEY:
        errors.append("ANTHROPIC_API_KEY não configurada no .env")

    # OpenAI API key é necessária para embeddings mesmo usando Anthropic
    if not OPENAI_API_KEY:
        errors.append("OPENAI_API_KEY necessária para embeddings (mesmo usando Claude)")

    return len(errors) == 0, errors


# ============================================
# EXIBIR CONFIGURAÇÃO (DEBUG)
# ============================================
if __name__ == "__main__":
    print("=" * 50)
    print("HemaTutor - Configuração Atual")
    print("=" * 50)
    print(f"LLM Provider: {LLM_PROVIDER}")
    print(f"LLM Model: {OPENAI_MODEL if LLM_PROVIDER == 'openai' else ANTHROPIC_MODEL}")
    print(f"VectorStore: {VECTORSTORE_TYPE}")
    print(f"Embedding Model: {EMBEDDING_MODEL}")
    print(f"Chunk Size: {CHUNK_SIZE}")
    print(f"Chunk Overlap: {CHUNK_OVERLAP}")
    print(f"Retriever K: {RETRIEVER_K}")
    print("=" * 50)

    is_valid, errors = validate_config()
    if is_valid:
        print("✓ Configuração válida!")
    else:
        print("✗ Erros de configuração:")
        for error in errors:
            print(f"  - {error}")

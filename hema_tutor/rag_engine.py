"""
rag_engine.py - Motor de RAG do HemaTutor

Este módulo é o coração do sistema, responsável por:
- Ingestão e processamento de PDFs (chunking com overlap)
- Criação e persistência de embeddings (FAISS ou ChromaDB)
- Busca semântica filtrada por trilha
- Geração de lições e quizzes via LLM com RAG
- Extração de trilhas do índice do PDF
"""

import os
import json
import hashlib
import re
from pathlib import Path
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field

# LangChain imports
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_community.vectorstores import FAISS
from langchain_community.vectorstores import Chroma
from langchain.schema import Document, HumanMessage, SystemMessage
from langchain_core.vectorstores import VectorStore

# Imports locais
from config import (
    OPENAI_API_KEY,
    ANTHROPIC_API_KEY,
    UPLOADS_DIR,
    VECTORSTORES_DIR,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    RETRIEVER_K,
    VECTORSTORE_TYPE,
    EMBEDDING_MODEL,
    EMBEDDING_PROVIDER,
    EMBEDDING_MODEL_LOCAL,
    LLM_PROVIDER,
    OPENAI_MODEL,
    ANTHROPIC_MODEL,
    LLM_TEMPERATURE,
    LLM_MAX_TOKENS,
    DEFAULT_TRACKS,
    QUESTIONS_PER_QUIZ,
)
from prompts import (
    SYSTEM_PROMPT_PROFESSOR,
    get_lesson_prompt,
    get_quiz_prompt,
    get_qa_prompt,
    get_track_extraction_prompt,
)


# ============================================
# DATA CLASSES
# ============================================
@dataclass
class QuizQuestion:
    """Representa uma questão do quiz."""
    id: int
    question: str
    options: Dict[str, str]
    correct_answer: str
    explanation: str


@dataclass
class Lesson:
    """Representa uma lição gerada."""
    track: str
    content: str
    quiz: List[QuizQuestion] = field(default_factory=list)
    sources: List[str] = field(default_factory=list)


@dataclass
class Track:
    """Representa uma trilha de aprendizado."""
    name: str
    description: str = ""
    chapters: List[str] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)


# ============================================
# CLASSE PRINCIPAL DO RAG ENGINE
# ============================================
class RAGEngine:
    """
    Motor de Retrieval-Augmented Generation para o HemaTutor.

    Esta classe encapsula toda a lógica de:
    - Processamento de PDFs
    - Criação de embeddings
    - Busca semântica
    - Geração de conteúdo educacional
    """

    def __init__(self):
        """Inicializa o RAG Engine com as configurações do config.py."""
        # Inicializa embeddings baseado no provider
        self.embeddings = self._initialize_embeddings()
        self.vectorstore: Optional[VectorStore] = None
        self.current_pdf_hash: Optional[str] = None
        self.tracks: List[Track] = []

        # Inicializa o LLM baseado no provider
        self.llm = self._initialize_llm()

        # Text splitter para chunking
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )

    def _initialize_embeddings(self):
        """
        Inicializa o modelo de embeddings baseado na configuração.

        Returns:
            OpenAIEmbeddings ou HuggingFaceEmbeddings
        """
        if EMBEDDING_PROVIDER == "local":
            # Embeddings locais via HuggingFace (GRATUITO!)
            from langchain_huggingface import HuggingFaceEmbeddings
            return HuggingFaceEmbeddings(
                model_name=EMBEDDING_MODEL_LOCAL,
                model_kwargs={'device': 'cpu'},
                encode_kwargs={'normalize_embeddings': True}
            )
        else:
            # Embeddings OpenAI
            return OpenAIEmbeddings(
                model=EMBEDDING_MODEL,
                openai_api_key=OPENAI_API_KEY
            )

    def _initialize_llm(self):
        """
        Inicializa o modelo de linguagem baseado na configuração.

        Returns:
            ChatOpenAI ou ChatAnthropic dependendo do LLM_PROVIDER
        """
        if LLM_PROVIDER == "openai":
            return ChatOpenAI(
                model=OPENAI_MODEL,
                temperature=LLM_TEMPERATURE,
                max_tokens=LLM_MAX_TOKENS,
                openai_api_key=OPENAI_API_KEY
            )
        else:
            return ChatAnthropic(
                model=ANTHROPIC_MODEL,
                temperature=LLM_TEMPERATURE,
                max_tokens=LLM_MAX_TOKENS,
                anthropic_api_key=ANTHROPIC_API_KEY
            )

    def _get_pdf_hash(self, pdf_path: str) -> str:
        """
        Gera um hash MD5 do arquivo PDF para identificação única.

        Args:
            pdf_path: Caminho do arquivo PDF

        Returns:
            str: Hash MD5 do arquivo
        """
        with open(pdf_path, "rb") as f:
            return hashlib.md5(f.read()).hexdigest()[:12]

    def _get_vectorstore_path(self, pdf_hash: str) -> Path:
        """
        Retorna o caminho do diretório do VectorStore para um PDF.

        Args:
            pdf_hash: Hash do PDF

        Returns:
            Path: Caminho do diretório
        """
        return VECTORSTORES_DIR / f"{VECTORSTORE_TYPE}_{pdf_hash}"

    def _extract_track_from_content(self, text: str) -> str:
        """
        Tenta identificar a trilha de um chunk baseado em seu conteúdo.

        Args:
            text: Texto do chunk

        Returns:
            str: Nome da trilha identificada ou "Geral"
        """
        text_lower = text.lower()

        # Mapeamento de keywords para trilhas
        track_keywords = {
            "Anemias": [
                "anemia", "hemoglobina", "eritrócito", "ferritina", "ferro",
                "vitamina b12", "folato", "hemólise", "reticulócito", "hematócrito"
            ],
            "Hemostasia e Trombose": [
                "coagulação", "hemostasia", "trombose", "anticoagulante",
                "plaqueta", "fibrinogênio", "protrombina", "heparina", "warfarina",
                "trombofilia", "sangramento", "hemofilia"
            ],
            "Neoplasias Hematológicas": [
                "leucemia", "linfoma", "mieloma", "neoplasia", "maligno",
                "quimioterapia", "blastos", "hodgkin", "mielodisplasia"
            ],
            "Transplante de Medula Óssea": [
                "transplante", "medula óssea", "células-tronco", "enxerto",
                "condicionamento", "gvhd", "alogênico", "autólogo"
            ],
            "Hemoglobinopatias": [
                "falciforme", "talassemia", "hemoglobina s", "drepanocitose",
                "hemoglobinopatia", "eletroforese"
            ],
            "Distúrbios Leucocitários": [
                "leucócito", "neutropenia", "leucocitose", "neutrofilia",
                "linfocitose", "eosinofilia"
            ],
            "Medicina Transfusional": [
                "transfusão", "hemoderivado", "concentrado de hemácias",
                "plaquetas", "plasma", "tipagem", "compatibilidade", "banco de sangue"
            ],
        }

        # Conta matches para cada trilha
        track_scores = {}
        for track, keywords in track_keywords.items():
            score = sum(1 for kw in keywords if kw in text_lower)
            if score > 0:
                track_scores[track] = score

        # Retorna a trilha com maior score
        if track_scores:
            return max(track_scores, key=track_scores.get)
        return "Geral"

    def _extract_page_number(self, doc: Document) -> Optional[int]:
        """
        Extrai o número da página dos metadados do documento.

        Args:
            doc: Documento do LangChain

        Returns:
            int ou None: Número da página
        """
        return doc.metadata.get("page", None)

    # ============================================
    # INGESTÃO DE PDF
    # ============================================
    def ingest_pdf(self, pdf_path: str, progress_callback=None) -> bool:
        """
        Processa um PDF, cria embeddings e persiste o VectorStore.

        Args:
            pdf_path: Caminho do arquivo PDF
            progress_callback: Função de callback para atualizar progresso (opcional)

        Returns:
            bool: True se sucesso, False se erro
        """
        try:
            # 1. Calcula hash do PDF
            pdf_hash = self._get_pdf_hash(pdf_path)
            self.current_pdf_hash = pdf_hash
            vs_path = self._get_vectorstore_path(pdf_hash)

            if progress_callback:
                progress_callback(0.1, "Verificando cache...")

            # 2. Verifica se já existe VectorStore
            if self._vectorstore_exists(vs_path):
                if progress_callback:
                    progress_callback(1.0, "VectorStore encontrado em cache!")
                self.vectorstore = self._load_vectorstore(vs_path)
                self._load_tracks_from_vectorstore()
                return True

            if progress_callback:
                progress_callback(0.2, "Carregando PDF...")

            # 3. Carrega o PDF
            loader = PyPDFLoader(pdf_path)
            pages = loader.load()

            if progress_callback:
                progress_callback(0.4, f"PDF carregado: {len(pages)} páginas")

            # 4. Chunking com metadados
            if progress_callback:
                progress_callback(0.5, "Criando chunks...")

            documents = []
            for page in pages:
                page_num = page.metadata.get("page", 0) + 1  # 1-indexed
                chunks = self.text_splitter.split_text(page.page_content)

                for i, chunk in enumerate(chunks):
                    # Identifica a trilha do chunk
                    track = self._extract_track_from_content(chunk)

                    doc = Document(
                        page_content=chunk,
                        metadata={
                            "page": page_num,
                            "chunk_index": i,
                            "track": track,
                            "source": os.path.basename(pdf_path),
                            "pdf_hash": pdf_hash
                        }
                    )
                    documents.append(doc)

            if progress_callback:
                progress_callback(0.7, f"Criados {len(documents)} chunks. Gerando embeddings...")

            # 5. Cria VectorStore
            if VECTORSTORE_TYPE == "faiss":
                self.vectorstore = FAISS.from_documents(documents, self.embeddings)
                # Persiste FAISS
                vs_path.mkdir(parents=True, exist_ok=True)
                self.vectorstore.save_local(str(vs_path))
            else:
                # ChromaDB
                self.vectorstore = Chroma.from_documents(
                    documents,
                    self.embeddings,
                    persist_directory=str(vs_path)
                )

            if progress_callback:
                progress_callback(0.9, "Extraindo trilhas...")

            # 6. Extrai trilhas
            self._extract_tracks_from_documents(documents)

            if progress_callback:
                progress_callback(1.0, "Processamento concluído!")

            return True

        except Exception as e:
            print(f"Erro na ingestão do PDF: {e}")
            raise e

    def _vectorstore_exists(self, vs_path: Path) -> bool:
        """Verifica se um VectorStore já existe."""
        if VECTORSTORE_TYPE == "faiss":
            return (vs_path / "index.faiss").exists()
        else:
            return (vs_path / "chroma.sqlite3").exists()

    def _load_vectorstore(self, vs_path: Path) -> VectorStore:
        """Carrega um VectorStore existente."""
        if VECTORSTORE_TYPE == "faiss":
            return FAISS.load_local(
                str(vs_path),
                self.embeddings,
                allow_dangerous_deserialization=True
            )
        else:
            return Chroma(
                persist_directory=str(vs_path),
                embedding_function=self.embeddings
            )

    def load_vectorstore(self, pdf_hash: str = None) -> Optional[VectorStore]:
        """
        Carrega um VectorStore existente pelo hash do PDF.

        Args:
            pdf_hash: Hash do PDF (usa o atual se não especificado)

        Returns:
            VectorStore ou None
        """
        if pdf_hash is None:
            pdf_hash = self.current_pdf_hash

        if pdf_hash is None:
            return None

        vs_path = self._get_vectorstore_path(pdf_hash)
        if self._vectorstore_exists(vs_path):
            self.vectorstore = self._load_vectorstore(vs_path)
            self._load_tracks_from_vectorstore()
            return self.vectorstore
        return None

    def _load_tracks_from_vectorstore(self):
        """Extrai as trilhas únicas dos metadados do VectorStore."""
        if self.vectorstore is None:
            return

        # Busca alguns documentos para extrair trilhas
        try:
            if VECTORSTORE_TYPE == "faiss":
                # Para FAISS, usa o docstore
                docs = list(self.vectorstore.docstore._dict.values())
            else:
                # Para Chroma, faz uma busca
                results = self.vectorstore.similarity_search("hematologia", k=100)
                docs = results

            tracks_set = set()
            for doc in docs:
                track = doc.metadata.get("track", "Geral")
                tracks_set.add(track)

            self.tracks = [Track(name=t) for t in sorted(tracks_set)]
        except Exception as e:
            print(f"Erro ao carregar trilhas: {e}")
            self.tracks = [Track(name=t) for t in DEFAULT_TRACKS]

    def _extract_tracks_from_documents(self, documents: List[Document]):
        """Extrai trilhas únicas dos documentos processados."""
        tracks_set = set()
        for doc in documents:
            track = doc.metadata.get("track", "Geral")
            tracks_set.add(track)

        self.tracks = [Track(name=t) for t in sorted(tracks_set)]

    # ============================================
    # BUSCA E RECUPERAÇÃO
    # ============================================
    def search(
        self,
        query: str,
        k: int = RETRIEVER_K,
        track_filter: Optional[str] = None
    ) -> List[Document]:
        """
        Busca documentos relevantes no VectorStore.

        Args:
            query: Texto da busca
            k: Número de resultados
            track_filter: Filtrar por trilha específica (opcional)

        Returns:
            List[Document]: Documentos mais relevantes
        """
        if self.vectorstore is None:
            return []

        # Busca inicial
        results = self.vectorstore.similarity_search(query, k=k * 2)

        # Filtra por trilha se especificado
        if track_filter and track_filter != "Todas":
            results = [
                doc for doc in results
                if doc.metadata.get("track", "").lower() == track_filter.lower()
            ]

        return results[:k]

    def get_context_from_docs(self, docs: List[Document]) -> str:
        """
        Formata os documentos recuperados em um contexto para o LLM.

        Args:
            docs: Lista de documentos

        Returns:
            str: Contexto formatado
        """
        context_parts = []
        for i, doc in enumerate(docs, 1):
            page = doc.metadata.get("page", "?")
            track = doc.metadata.get("track", "?")
            context_parts.append(
                f"[Trecho {i} | Página {page} | Trilha: {track}]\n{doc.page_content}\n"
            )
        return "\n---\n".join(context_parts)

    # ============================================
    # GERAÇÃO DE CONTEÚDO
    # ============================================
    def generate_lesson(self, track: str) -> Lesson:
        """
        Gera uma lição estruturada para uma trilha específica.

        Args:
            track: Nome da trilha

        Returns:
            Lesson: Objeto contendo lição e quiz
        """
        if self.vectorstore is None:
            raise ValueError("VectorStore não carregado. Processe um PDF primeiro.")

        # 1. Busca contexto relevante para a trilha
        query = f"Conceitos fundamentais de {track} em hematologia"
        docs = self.search(query, k=RETRIEVER_K, track_filter=track)

        if not docs:
            # Fallback: busca sem filtro de trilha
            docs = self.search(query, k=RETRIEVER_K)

        context = self.get_context_from_docs(docs)

        # 2. Gera a lição
        lesson_prompt = get_lesson_prompt(track, context)
        messages = [
            SystemMessage(content=SYSTEM_PROMPT_PROFESSOR),
            HumanMessage(content=lesson_prompt)
        ]

        response = self.llm.invoke(messages)
        lesson_content = response.content

        # 3. Gera o quiz
        quiz_prompt = get_quiz_prompt(context, lesson_content, QUESTIONS_PER_QUIZ)
        quiz_messages = [
            SystemMessage(content=SYSTEM_PROMPT_PROFESSOR),
            HumanMessage(content=quiz_prompt)
        ]

        quiz_response = self.llm.invoke(quiz_messages)
        quiz_questions = self._parse_quiz_response(quiz_response.content)

        # 4. Coleta fontes
        sources = list(set(
            f"Página {doc.metadata.get('page', '?')}"
            for doc in docs
        ))

        return Lesson(
            track=track,
            content=lesson_content,
            quiz=quiz_questions,
            sources=sources
        )

    def _parse_quiz_response(self, response: str) -> List[QuizQuestion]:
        """
        Parseia a resposta do LLM para extrair as questões do quiz.

        Args:
            response: Resposta do LLM em formato JSON

        Returns:
            List[QuizQuestion]: Lista de questões parseadas
        """
        questions = []

        try:
            # Tenta extrair JSON da resposta
            json_match = re.search(r'\{[\s\S]*"questions"[\s\S]*\}', response)
            if json_match:
                data = json.loads(json_match.group())
                for q in data.get("questions", []):
                    questions.append(QuizQuestion(
                        id=q.get("id", len(questions) + 1),
                        question=q.get("question", ""),
                        options=q.get("options", {}),
                        correct_answer=q.get("correct_answer", "A"),
                        explanation=q.get("explanation", "")
                    ))
        except json.JSONDecodeError:
            # Fallback: cria questão placeholder
            questions.append(QuizQuestion(
                id=1,
                question="Erro ao gerar questões. Tente novamente.",
                options={"A": "Opção A", "B": "Opção B", "C": "Opção C", "D": "Opção D"},
                correct_answer="A",
                explanation="Houve um erro no processamento."
            ))

        return questions

    def answer_question(self, question: str, track_filter: Optional[str] = None) -> str:
        """
        Responde uma pergunta livre do usuário usando RAG.

        Args:
            question: Pergunta do usuário
            track_filter: Filtrar por trilha (opcional)

        Returns:
            str: Resposta gerada
        """
        if self.vectorstore is None:
            return "Por favor, processe um PDF primeiro para que eu possa responder suas perguntas."

        # Busca contexto
        docs = self.search(question, k=RETRIEVER_K, track_filter=track_filter)
        context = self.get_context_from_docs(docs)

        # Gera resposta
        qa_prompt = get_qa_prompt(context, question)
        messages = [
            SystemMessage(content=SYSTEM_PROMPT_PROFESSOR),
            HumanMessage(content=qa_prompt)
        ]

        response = self.llm.invoke(messages)
        return response.content

    # ============================================
    # FUNÇÕES DE TRILHA
    # ============================================
    def get_tracks(self) -> List[str]:
        """
        Retorna a lista de trilhas disponíveis.

        Returns:
            List[str]: Nomes das trilhas
        """
        if self.tracks:
            return [t.name for t in self.tracks]
        return DEFAULT_TRACKS

    def get_tracks_from_pdf(self, pdf_path: str) -> List[str]:
        """
        Extrai trilhas das primeiras páginas de um PDF.

        Args:
            pdf_path: Caminho do PDF

        Returns:
            List[str]: Lista de trilhas identificadas
        """
        try:
            loader = PyPDFLoader(pdf_path)
            pages = loader.load()

            # Pega as primeiras 10 páginas (índice/TOC)
            toc_content = "\n".join([
                p.page_content for p in pages[:10]
            ])

            # Usa LLM para extrair trilhas
            prompt = get_track_extraction_prompt(toc_content)
            messages = [
                SystemMessage(content="Você é um assistente que analisa índices de livros."),
                HumanMessage(content=prompt)
            ]

            response = self.llm.invoke(messages)

            # Tenta parsear JSON
            json_match = re.search(r'\{[\s\S]*"tracks"[\s\S]*\}', response.content)
            if json_match:
                data = json.loads(json_match.group())
                tracks = [t["name"] for t in data.get("tracks", [])]
                if tracks:
                    return tracks

        except Exception as e:
            print(f"Erro ao extrair trilhas: {e}")

        return DEFAULT_TRACKS

    # ============================================
    # UTILITÁRIOS
    # ============================================
    def get_stats(self) -> Dict[str, Any]:
        """
        Retorna estatísticas do VectorStore atual.

        Returns:
            Dict: Estatísticas incluindo número de chunks, trilhas, etc.
        """
        stats = {
            "vectorstore_loaded": self.vectorstore is not None,
            "vectorstore_type": VECTORSTORE_TYPE,
            "num_tracks": len(self.tracks),
            "tracks": self.get_tracks(),
            "llm_provider": LLM_PROVIDER,
            "llm_model": OPENAI_MODEL if LLM_PROVIDER == "openai" else ANTHROPIC_MODEL,
        }

        if self.vectorstore and VECTORSTORE_TYPE == "faiss":
            try:
                stats["num_chunks"] = len(self.vectorstore.docstore._dict)
            except:
                stats["num_chunks"] = "N/A"

        return stats

    def clear_vectorstore(self, pdf_hash: str = None):
        """
        Remove um VectorStore persistido.

        Args:
            pdf_hash: Hash do PDF (usa o atual se não especificado)
        """
        import shutil

        if pdf_hash is None:
            pdf_hash = self.current_pdf_hash

        if pdf_hash:
            vs_path = self._get_vectorstore_path(pdf_hash)
            if vs_path.exists():
                shutil.rmtree(vs_path)
                print(f"VectorStore removido: {vs_path}")

        self.vectorstore = None
        self.current_pdf_hash = None


# ============================================
# INSTÂNCIA SINGLETON
# ============================================
_engine_instance: Optional[RAGEngine] = None


def get_rag_engine() -> RAGEngine:
    """
    Retorna a instância singleton do RAG Engine.

    Returns:
        RAGEngine: Instância do motor RAG
    """
    global _engine_instance
    if _engine_instance is None:
        _engine_instance = RAGEngine()
    return _engine_instance

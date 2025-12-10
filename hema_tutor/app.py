"""
app.py - Interface Streamlit do HemaTutor

Este módulo implementa a interface do usuário completa com:
- Sidebar: Upload de PDF, processamento, dashboard de progresso
- Área principal: Seleção de trilhas, geração de lições, quiz interativo
- Persistência via st.session_state
"""

import os
import streamlit as st
from pathlib import Path
import time

# Imports locais
from config import (
    UPLOADS_DIR,
    validate_config,
    LLM_PROVIDER,
    OPENAI_MODEL,
    ANTHROPIC_MODEL,
    VECTORSTORE_TYPE,
)
from rag_engine import get_rag_engine, Lesson, QuizQuestion
from prompts import get_feedback_message, get_encouragement_message

# ============================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================
st.set_page_config(
    page_title="HemaTutor - Plataforma de Ensino em Hematologia",
    page_icon="🩸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# CSS CUSTOMIZADO
# ============================================
st.markdown("""
<style>
    /* Estilo geral */
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #B22222;
        text-align: center;
        margin-bottom: 1rem;
    }

    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }

    /* Cards de estatísticas */
    .stat-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }

    .stat-number {
        font-size: 2rem;
        font-weight: bold;
    }

    .stat-label {
        font-size: 0.9rem;
        opacity: 0.9;
    }

    /* Quiz styling */
    .quiz-question {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #B22222;
        margin: 1rem 0;
    }

    /* Lesson styling */
    .lesson-content {
        background: #ffffff;
        padding: 2rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }

    /* Progress bar customization */
    .stProgress > div > div > div > div {
        background-color: #B22222;
    }

    /* Sidebar styling */
    .sidebar-section {
        background: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)


# ============================================
# INICIALIZAÇÃO DO SESSION STATE
# ============================================
def init_session_state():
    """Inicializa todas as variáveis do session_state."""
    defaults = {
        # Estado do PDF
        "pdf_processed": False,
        "pdf_name": None,
        "pdf_hash": None,

        # Trilhas e navegação
        "current_track": None,
        "available_tracks": [],

        # Lições
        "current_lesson": None,
        "current_lesson_index": 0,
        "lessons_done": [],

        # Quiz
        "quiz_active": False,
        "quiz_answers": {},
        "quiz_submitted": False,
        "quiz_results": None,

        # Histórico e pontuação
        "quiz_history": [],
        "score_total": 0,
        "questions_total": 0,

        # UI State
        "show_lesson": False,
        "processing": False,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


# ============================================
# SIDEBAR: UPLOAD E STATUS
# ============================================
def render_sidebar():
    """Renderiza a sidebar com upload, processamento e dashboard."""

    st.sidebar.markdown("## 🩸 HemaTutor")
    st.sidebar.markdown("*Plataforma de Ensino em Hematologia*")
    st.sidebar.markdown("---")

    # --- SEÇÃO 1: Upload de PDF ---
    st.sidebar.markdown("### 📄 Material de Estudo")

    uploaded_file = st.sidebar.file_uploader(
        "Faça upload do PDF (ASH-SAP)",
        type=["pdf"],
        help="Envie o PDF do ASH-SAP ou outro material de hematologia"
    )

    if uploaded_file is not None:
        # Salva o arquivo
        file_path = UPLOADS_DIR / uploaded_file.name
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        st.sidebar.success(f"✓ Arquivo: {uploaded_file.name}")

        # Botão de processamento
        if st.sidebar.button("🔄 Processar Material", type="primary", use_container_width=True):
            process_pdf(str(file_path))

    # Status do processamento
    if st.session_state.pdf_processed:
        st.sidebar.markdown(f"**Material ativo:** {st.session_state.pdf_name}")
        st.sidebar.markdown(f"**Trilhas:** {len(st.session_state.available_tracks)}")

    st.sidebar.markdown("---")

    # --- SEÇÃO 2: Dashboard de Progresso ---
    st.sidebar.markdown("### 📊 Seu Progresso")

    # Progresso das lições
    total_tracks = len(st.session_state.available_tracks) or 1
    lessons_completed = len(st.session_state.lessons_done)
    progress_pct = min(lessons_completed / total_tracks, 1.0)

    st.sidebar.markdown("**Lições Concluídas**")
    st.sidebar.progress(progress_pct)
    st.sidebar.markdown(f"{lessons_completed} de {total_tracks} trilhas estudadas")

    # Score do Quiz
    st.sidebar.markdown("---")
    st.sidebar.markdown("**🎯 Score de Acertos**")

    questions_total = st.session_state.questions_total
    score_total = st.session_state.score_total

    if questions_total > 0:
        accuracy = (score_total / questions_total) * 100
        st.sidebar.metric(
            label="Taxa de Acerto",
            value=f"{accuracy:.1f}%",
            delta=f"{score_total}/{questions_total} questões"
        )
    else:
        st.sidebar.info("Complete quizzes para ver seu score!")

    # --- SEÇÃO 3: Trilhas Disponíveis ---
    if st.session_state.available_tracks:
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 🛤️ Trilhas Disponíveis")
        for track in st.session_state.available_tracks:
            icon = "✅" if track in st.session_state.lessons_done else "📚"
            st.sidebar.markdown(f"{icon} {track}")

    # --- SEÇÃO 4: Configuração ---
    st.sidebar.markdown("---")
    with st.sidebar.expander("⚙️ Configurações"):
        st.markdown(f"**LLM:** {LLM_PROVIDER.upper()}")
        model = OPENAI_MODEL if LLM_PROVIDER == "openai" else ANTHROPIC_MODEL
        st.markdown(f"**Modelo:** {model}")
        st.markdown(f"**VectorStore:** {VECTORSTORE_TYPE.upper()}")

        # Botão de reset
        if st.button("🗑️ Resetar Progresso", use_container_width=True):
            reset_progress()
            st.rerun()


def process_pdf(file_path: str):
    """Processa o PDF e atualiza o session_state."""
    st.session_state.processing = True

    progress_bar = st.sidebar.progress(0)
    status_text = st.sidebar.empty()

    def update_progress(value: float, message: str):
        progress_bar.progress(value)
        status_text.text(message)

    try:
        engine = get_rag_engine()
        engine.ingest_pdf(file_path, progress_callback=update_progress)

        # Atualiza session_state
        st.session_state.pdf_processed = True
        st.session_state.pdf_name = os.path.basename(file_path)
        st.session_state.pdf_hash = engine.current_pdf_hash
        st.session_state.available_tracks = engine.get_tracks()

        time.sleep(0.5)  # Pequena pausa para feedback visual
        st.sidebar.success("✅ Material processado com sucesso!")

    except Exception as e:
        st.sidebar.error(f"❌ Erro: {str(e)}")

    finally:
        st.session_state.processing = False
        progress_bar.empty()
        status_text.empty()

    st.rerun()


def reset_progress():
    """Reseta o progresso do usuário."""
    st.session_state.lessons_done = []
    st.session_state.quiz_history = []
    st.session_state.score_total = 0
    st.session_state.questions_total = 0
    st.session_state.current_lesson = None
    st.session_state.quiz_active = False
    st.session_state.quiz_submitted = False


# ============================================
# ÁREA PRINCIPAL: LIÇÕES E QUIZ
# ============================================
def render_main_area():
    """Renderiza a área principal com lições e quiz."""

    # Header
    st.markdown('<h1 class="main-header">🩸 HemaTutor</h1>', unsafe_allow_html=True)
    st.markdown(
        '<p class="sub-header">Plataforma Adaptativa de Ensino em Hematologia</p>',
        unsafe_allow_html=True
    )

    # Validação de configuração
    is_valid, errors = validate_config()
    if not is_valid:
        st.error("⚠️ **Configuração Incompleta**")
        for error in errors:
            st.warning(f"• {error}")
        st.info("Configure as variáveis de ambiente no arquivo `.env`")
        return

    # Verifica se há PDF processado
    if not st.session_state.pdf_processed:
        render_welcome_screen()
        return

    # Tabs principais
    tab1, tab2, tab3 = st.tabs(["📚 Lição do Dia", "❓ Perguntas Livres", "📈 Histórico"])

    with tab1:
        render_lesson_tab()

    with tab2:
        render_qa_tab()

    with tab3:
        render_history_tab()


def render_welcome_screen():
    """Tela de boas-vindas quando não há PDF processado."""
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown("---")
        st.markdown("### 👋 Bem-vindo ao HemaTutor!")
        st.markdown("""
        O HemaTutor é uma plataforma de ensino adaptativa focada em **Hematologia**,
        baseada no conteúdo do **ASH-SAP** (American Society of Hematology Self-Assessment Program).

        **Para começar:**
        1. 📄 Faça upload do PDF na barra lateral
        2. 🔄 Clique em "Processar Material"
        3. 📚 Escolha uma trilha de aprendizado
        4. 🎯 Estude as lições e teste seu conhecimento!

        ---

        **Funcionalidades:**
        - 🛤️ **Trilhas de Aprendizado** organizadas por tema
        - 📖 **Lições Estruturadas** com teoria e aplicação clínica
        - 📝 **Quizzes Interativos** para testar conhecimento
        - 📊 **Acompanhamento de Progresso** em tempo real
        - 🤖 **IA Especialista** que responde apenas com base no material
        """)
        st.markdown("---")


def render_lesson_tab():
    """Renderiza a tab de Lição do Dia."""

    # Seleção de trilha
    st.markdown("### 🛤️ Escolha sua Trilha de Aprendizado")

    col1, col2 = st.columns([3, 1])

    with col1:
        selected_track = st.selectbox(
            "Selecione a trilha:",
            options=st.session_state.available_tracks,
            index=0 if st.session_state.available_tracks else None,
            help="Escolha o tema que deseja estudar"
        )

    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        generate_button = st.button(
            "📖 Gerar Lição",
            type="primary",
            use_container_width=True,
            disabled=not selected_track
        )

    if generate_button and selected_track:
        generate_lesson(selected_track)

    # Exibe a lição atual
    if st.session_state.current_lesson:
        render_lesson()


def generate_lesson(track: str):
    """Gera uma nova lição para a trilha selecionada."""
    with st.spinner(f"🔄 Gerando lição sobre {track}..."):
        try:
            engine = get_rag_engine()
            lesson = engine.generate_lesson(track)

            st.session_state.current_lesson = lesson
            st.session_state.current_track = track
            st.session_state.quiz_active = False
            st.session_state.quiz_submitted = False
            st.session_state.quiz_answers = {}
            st.session_state.show_lesson = True

        except Exception as e:
            st.error(f"❌ Erro ao gerar lição: {str(e)}")


def render_lesson():
    """Renderiza a lição atual."""
    lesson: Lesson = st.session_state.current_lesson

    st.markdown("---")
    st.markdown(f"## 📚 Lição: {lesson.track}")

    # Conteúdo da lição
    with st.container():
        st.markdown(lesson.content)

    # Fontes
    if lesson.sources:
        with st.expander("📄 Fontes consultadas"):
            st.markdown(", ".join(lesson.sources))

    st.markdown("---")

    # Seção do Quiz
    st.markdown("### 📝 Quiz - Teste seu Conhecimento")

    if not st.session_state.quiz_active and not st.session_state.quiz_submitted:
        if st.button("🎯 Iniciar Quiz", type="primary"):
            st.session_state.quiz_active = True
            st.rerun()

    elif st.session_state.quiz_active and not st.session_state.quiz_submitted:
        render_quiz(lesson.quiz)

    elif st.session_state.quiz_submitted:
        render_quiz_results(lesson.quiz)


def render_quiz(questions: list[QuizQuestion]):
    """Renderiza as questões do quiz."""

    st.info("Responda todas as questões e clique em 'Corrigir Quiz'")

    for i, q in enumerate(questions):
        st.markdown(f"""
        <div class="quiz-question">
            <strong>Questão {q.id}:</strong> {q.question}
        </div>
        """, unsafe_allow_html=True)

        # Opções
        answer = st.radio(
            f"Selecione a resposta para a questão {q.id}:",
            options=list(q.options.keys()),
            format_func=lambda x, q=q: f"{x}) {q.options[x]}",
            key=f"quiz_q_{q.id}",
            index=None
        )

        if answer:
            st.session_state.quiz_answers[q.id] = answer

        st.markdown("---")

    # Botão de correção
    all_answered = len(st.session_state.quiz_answers) == len(questions)

    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button(
            "✅ Corrigir Quiz",
            type="primary",
            use_container_width=True,
            disabled=not all_answered
        ):
            submit_quiz(questions)
            st.rerun()

    if not all_answered:
        st.warning(f"⚠️ Responda todas as {len(questions)} questões antes de corrigir.")


def submit_quiz(questions: list[QuizQuestion]):
    """Processa a submissão do quiz."""
    correct_count = 0
    results = []

    for q in questions:
        user_answer = st.session_state.quiz_answers.get(q.id)
        is_correct = user_answer == q.correct_answer

        if is_correct:
            correct_count += 1

        results.append({
            "question_id": q.id,
            "user_answer": user_answer,
            "correct_answer": q.correct_answer,
            "is_correct": is_correct,
            "explanation": q.explanation
        })

    # Atualiza scores
    st.session_state.score_total += correct_count
    st.session_state.questions_total += len(questions)

    # Marca trilha como concluída
    track = st.session_state.current_track
    if track and track not in st.session_state.lessons_done:
        st.session_state.lessons_done.append(track)

    # Salva no histórico
    st.session_state.quiz_history.append({
        "track": track,
        "score": correct_count,
        "total": len(questions),
        "results": results
    })

    st.session_state.quiz_results = results
    st.session_state.quiz_submitted = True
    st.session_state.quiz_active = False


def render_quiz_results(questions: list[QuizQuestion]):
    """Renderiza os resultados do quiz."""
    results = st.session_state.quiz_results
    correct_count = sum(1 for r in results if r["is_correct"])
    total = len(results)

    # Score visual
    score_pct = (correct_count / total) * 100

    if score_pct >= 70:
        st.success(f"🎉 **Excelente!** Você acertou {correct_count} de {total} questões ({score_pct:.0f}%)")
    elif score_pct >= 50:
        st.warning(f"📚 **Bom trabalho!** Você acertou {correct_count} de {total} questões ({score_pct:.0f}%)")
    else:
        st.error(f"📖 **Continue estudando!** Você acertou {correct_count} de {total} questões ({score_pct:.0f}%)")

    st.markdown(get_encouragement_message())

    # Detalhamento das respostas
    st.markdown("---")
    st.markdown("### 📋 Detalhamento das Respostas")

    for i, (q, r) in enumerate(zip(questions, results)):
        with st.expander(
            f"{'✅' if r['is_correct'] else '❌'} Questão {q.id}: {q.question[:50]}...",
            expanded=not r["is_correct"]
        ):
            st.markdown(f"**Sua resposta:** {r['user_answer']}) {q.options.get(r['user_answer'], 'N/A')}")
            st.markdown(f"**Resposta correta:** {r['correct_answer']}) {q.options[r['correct_answer']]}")
            st.markdown(f"**Explicação:** {r['explanation']}")

    # Botão para nova lição
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("📚 Estudar Outra Trilha", use_container_width=True):
            st.session_state.current_lesson = None
            st.session_state.quiz_submitted = False
            st.session_state.quiz_active = False
            st.session_state.quiz_answers = {}
            st.rerun()


def render_qa_tab():
    """Renderiza a tab de perguntas livres."""
    st.markdown("### ❓ Pergunte ao Professor HemaTutor")
    st.markdown("""
    Faça perguntas sobre hematologia e o Professor HemaTutor responderá
    com base **exclusivamente** no material do ASH-SAP.
    """)

    # Filtro por trilha
    track_filter = st.selectbox(
        "Filtrar por trilha (opcional):",
        options=["Todas"] + st.session_state.available_tracks,
        help="Filtre a busca por uma trilha específica"
    )

    # Campo de pergunta
    question = st.text_area(
        "Digite sua pergunta:",
        placeholder="Ex: Quais são os critérios diagnósticos para anemia ferropriva?",
        height=100
    )

    if st.button("🔍 Perguntar", type="primary", disabled=not question):
        with st.spinner("🤔 Consultando o material..."):
            try:
                engine = get_rag_engine()
                filter_track = track_filter if track_filter != "Todas" else None
                answer = engine.answer_question(question, filter_track)

                st.markdown("---")
                st.markdown("### 💬 Resposta do Professor HemaTutor")
                st.markdown(answer)

            except Exception as e:
                st.error(f"❌ Erro: {str(e)}")


def render_history_tab():
    """Renderiza a tab de histórico."""
    st.markdown("### 📈 Histórico de Estudos")

    if not st.session_state.quiz_history:
        st.info("📝 Você ainda não completou nenhum quiz. Estude uma trilha para ver seu histórico!")
        return

    # Estatísticas gerais
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Total de Quizzes",
            len(st.session_state.quiz_history)
        )

    with col2:
        accuracy = (st.session_state.score_total / st.session_state.questions_total * 100) \
            if st.session_state.questions_total > 0 else 0
        st.metric(
            "Taxa de Acerto Geral",
            f"{accuracy:.1f}%"
        )

    with col3:
        st.metric(
            "Trilhas Estudadas",
            len(st.session_state.lessons_done)
        )

    st.markdown("---")

    # Histórico detalhado
    st.markdown("### 📋 Quizzes Realizados")

    for i, quiz in enumerate(reversed(st.session_state.quiz_history)):
        score_pct = (quiz["score"] / quiz["total"]) * 100
        status = "✅" if score_pct >= 70 else "⚠️" if score_pct >= 50 else "❌"

        with st.expander(f"{status} {quiz['track']} - {quiz['score']}/{quiz['total']} ({score_pct:.0f}%)"):
            for r in quiz["results"]:
                icon = "✅" if r["is_correct"] else "❌"
                st.markdown(f"{icon} Q{r['question_id']}: {r['user_answer']} (Correto: {r['correct_answer']})")


# ============================================
# MAIN
# ============================================
def main():
    """Função principal do app."""
    # Inicializa session state
    init_session_state()

    # Renderiza componentes
    render_sidebar()
    render_main_area()


if __name__ == "__main__":
    main()

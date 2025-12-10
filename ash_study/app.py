"""
app.py - Interface Streamlit da ASH-SAP Study Platform
"""
import streamlit as st
import json
from datetime import datetime

from config import validate_config, DATA_DIR
from study_engine import get_study_engine
from models import LessonStatus, Licao
from prompts import CHAPTER_INFO

# ============================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================
st.set_page_config(
    page_title="ASH-SAP Study Platform",
    page_icon="🩸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# CSS
# ============================================
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: bold;
        color: #8B0000;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stat-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .stat-number {
        font-size: 2rem;
        font-weight: bold;
    }
    .trilha-card {
        border: 1px solid #ddd;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        transition: all 0.3s;
    }
    .trilha-card:hover {
        border-color: #8B0000;
        box-shadow: 0 2px 8px rgba(139, 0, 0, 0.2);
    }
    .question-box {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #8B0000;
        margin: 1rem 0;
    }
    .correct { color: #28a745; }
    .incorrect { color: #dc3545; }
</style>
""", unsafe_allow_html=True)


# ============================================
# SESSION STATE
# ============================================
def init_session_state():
    defaults = {
        "page": "dashboard",
        "current_trilha": None,
        "current_licao": None,
        "quiz_questions": [],
        "quiz_answers": {},
        "quiz_submitted": False,
        "show_lesson_content": False,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


# ============================================
# SIDEBAR
# ============================================
def render_sidebar():
    st.sidebar.markdown("## 🩸 ASH-SAP Study")
    st.sidebar.markdown("*Plataforma de Estudo Adaptativa*")
    st.sidebar.markdown("---")

    # Navegação
    st.sidebar.markdown("### 📍 Navegação")

    if st.sidebar.button("🏠 Dashboard", use_container_width=True):
        st.session_state.page = "dashboard"
        st.rerun()

    if st.sidebar.button("📚 Trilhas de Estudo", use_container_width=True):
        st.session_state.page = "trilhas"
        st.rerun()

    if st.sidebar.button("📊 Meu Progresso", use_container_width=True):
        st.session_state.page = "progresso"
        st.rerun()

    if st.sidebar.button("📥 Importar Lição", use_container_width=True):
        st.session_state.page = "importar"
        st.rerun()

    st.sidebar.markdown("---")

    # Estatísticas rápidas
    try:
        engine = get_study_engine()
        stats = engine.get_estatisticas()

        st.sidebar.markdown("### 📈 Resumo")
        st.sidebar.metric("Lições Concluídas", f"{stats['licoes_concluidas']}/{stats['total_licoes']}")
        st.sidebar.progress(stats['percentual'] / 100)
        st.sidebar.metric("Taxa de Acerto", f"{stats['taxa_acerto']}%")
    except Exception as e:
        st.sidebar.warning("Configure a API key")


# ============================================
# PÁGINAS
# ============================================
def render_dashboard():
    st.markdown('<h1 class="main-header">🩸 ASH-SAP Study Platform</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Plataforma Adaptativa de Estudo em Hematologia</p>', unsafe_allow_html=True)

    # Validação
    is_valid, errors = validate_config()
    if not is_valid:
        st.error("⚠️ **Configuração necessária**")
        for e in errors:
            st.warning(f"• {e}")
        st.info("Configure o arquivo `.env` com sua `ANTHROPIC_API_KEY`")
        return

    engine = get_study_engine()
    stats = engine.get_estatisticas()

    # Cards de estatísticas
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-number">{stats['licoes_concluidas']}</div>
            <div>Lições Concluídas</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-number">{stats['percentual']}%</div>
            <div>Progresso Geral</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-number">{stats['taxa_acerto']}%</div>
            <div>Taxa de Acerto</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-number">{stats['questoes_respondidas']}</div>
            <div>Questões Respondidas</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Ação rápida
    st.markdown("### 🚀 Começar a Estudar")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Continuar onde parou")
        prog = engine.get_progresso()
        if prog.trilha_atual:
            trilha = engine.get_trilha(prog.trilha_atual)
            if trilha:
                st.info(f"**Trilha atual:** {trilha.nome}")
                if st.button("▶️ Continuar Estudo", type="primary"):
                    st.session_state.current_trilha = prog.trilha_atual
                    st.session_state.page = "estudar"
                    st.rerun()
        else:
            st.info("Selecione uma trilha para começar!")

    with col2:
        st.markdown("#### Escolher trilha")
        trilhas = engine.get_trilhas()
        trilha_options = {t.nome: t.id for t in trilhas}
        selected = st.selectbox("Selecione uma trilha:", list(trilha_options.keys()))
        if st.button("📚 Ir para Trilha"):
            st.session_state.current_trilha = trilha_options[selected]
            st.session_state.page = "estudar"
            st.rerun()


def render_trilhas():
    st.markdown("## 📚 Trilhas de Estudo")
    st.markdown("Selecione uma trilha para ver os capítulos disponíveis.")
    st.markdown("---")

    engine = get_study_engine()
    trilhas = engine.get_trilhas()

    for trilha in trilhas:
        caps_concluidos = engine.get_capitulos_concluidos(trilha.id)
        total_caps = len(trilha.capitulos)
        progresso = len(caps_concluidos) / total_caps if total_caps > 0 else 0

        with st.expander(f"**{trilha.nome}** ({len(caps_concluidos)}/{total_caps} capítulos)"):
            st.progress(progresso)

            # Lista de capítulos
            for cap in trilha.capitulos:
                info = CHAPTER_INFO.get(cap, {"titulo": f"Capítulo {cap}"})
                status = "✅" if cap in caps_concluidos else "📖"
                st.markdown(f"{status} **Cap. {cap}:** {info['titulo']}")

            if st.button(f"Estudar {trilha.nome}", key=f"btn_{trilha.id}"):
                st.session_state.current_trilha = trilha.id
                st.session_state.page = "estudar"
                st.rerun()


def render_estudar():
    trilha_id = st.session_state.current_trilha
    if not trilha_id:
        st.warning("Selecione uma trilha primeiro!")
        return

    engine = get_study_engine()
    trilha = engine.get_trilha(trilha_id)

    if not trilha:
        st.error("Trilha não encontrada!")
        return

    st.markdown(f"## 📖 {trilha.nome}")

    # Seleciona próximo capítulo
    caps_concluidos = engine.get_capitulos_concluidos(trilha_id)
    caps_pendentes = [c for c in trilha.capitulos if c not in caps_concluidos]

    if not caps_pendentes:
        st.success("🎉 Parabéns! Você concluiu todos os capítulos desta trilha!")
        if st.button("← Voltar às Trilhas"):
            st.session_state.page = "trilhas"
            st.rerun()
        return

    # Seleção de capítulo
    col1, col2 = st.columns([3, 1])
    with col1:
        cap_options = {f"Cap. {c}: {CHAPTER_INFO.get(c, {}).get('titulo', '')}": c for c in caps_pendentes}
        selected_cap_name = st.selectbox("Selecione o capítulo:", list(cap_options.keys()))
        selected_cap = cap_options[selected_cap_name]

    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        gerar_btn = st.button("📝 Gerar Lição", type="primary")

    # Gera lição
    if gerar_btn or st.session_state.current_licao:
        if gerar_btn:
            with st.spinner("🤖 Gerando lição com Claude..."):
                licao = engine.gerar_licao(trilha_id, selected_cap)
                st.session_state.current_licao = licao
                st.session_state.show_lesson_content = True
                st.session_state.quiz_submitted = False
                st.session_state.quiz_answers = {}

        licao = st.session_state.current_licao

        if licao and st.session_state.show_lesson_content:
            st.markdown("---")
            st.markdown(f"### 📚 {licao.titulo}")

            # Conteúdo da lição
            with st.expander("📖 Ver Conteúdo da Lição", expanded=True):
                st.markdown(licao.conteudo)

            st.markdown("---")

            # Quiz
            if not st.session_state.quiz_questions:
                if st.button("📝 Gerar Quiz", type="primary"):
                    with st.spinner("Gerando questões..."):
                        questions = engine.gerar_quiz(licao)
                        st.session_state.quiz_questions = questions
                        st.rerun()
            else:
                render_quiz(engine, licao)


def render_quiz(engine, licao):
    st.markdown("### 📝 Quiz de Avaliação")

    questions = st.session_state.quiz_questions

    if not st.session_state.quiz_submitted:
        for q in questions:
            st.markdown(f"""
            <div class="question-box">
                <strong>Questão {q.numero}:</strong> {q.tema}<br>
                <em>{q.cenario}</em>
            </div>
            """, unsafe_allow_html=True)

            answer = st.radio(
                f"Selecione a resposta:",
                options=list(q.opcoes.keys()),
                format_func=lambda x, q=q: f"{x}) {q.opcoes[x]}",
                key=f"q_{q.numero}",
                index=None
            )

            if answer:
                st.session_state.quiz_answers[q.numero] = answer

        if len(st.session_state.quiz_answers) == len(questions):
            if st.button("✅ Corrigir Quiz", type="primary"):
                avaliacao = engine.avaliar_quiz(
                    licao,
                    questions,
                    st.session_state.quiz_answers
                )
                licao.avaliacao = avaliacao
                st.session_state.quiz_submitted = True
                st.rerun()
        else:
            st.warning(f"Responda todas as {len(questions)} questões para corrigir.")

    else:
        # Mostra resultados
        avaliacao = licao.avaliacao

        if avaliacao.taxa_acerto >= 85:
            st.success(f"🎉 **Excelente!** Você acertou {avaliacao.questoes_corretas}/{avaliacao.total_questoes} ({avaliacao.taxa_acerto:.0f}%)")
        elif avaliacao.taxa_acerto >= 70:
            st.warning(f"📚 **Bom trabalho!** Você acertou {avaliacao.questoes_corretas}/{avaliacao.total_questoes} ({avaliacao.taxa_acerto:.0f}%)")
        else:
            st.error(f"📖 **Revise o conteúdo!** Você acertou {avaliacao.questoes_corretas}/{avaliacao.total_questoes} ({avaliacao.taxa_acerto:.0f}%)")

        # Detalhes
        with st.expander("📋 Ver Detalhes das Respostas"):
            for q in avaliacao.questoes:
                icon = "✅" if q.resultado == "correta" else "❌"
                st.markdown(f"**{icon} Questão {q.numero}:** {q.tema}")
                st.markdown(f"Sua resposta: **{q.resposta_aluno}** | Correta: **{q.resposta_correta}**")
                st.markdown(f"_{q.explicacao}_")
                st.markdown("---")

        # Ações
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Concluir e Avançar"):
                engine.concluir_licao(licao)
                st.session_state.current_licao = None
                st.session_state.quiz_questions = []
                st.session_state.quiz_submitted = False
                st.session_state.quiz_answers = {}
                st.success("Lição concluída!")
                st.rerun()

        with col2:
            if st.button("🔄 Refazer Quiz"):
                st.session_state.quiz_submitted = False
                st.session_state.quiz_answers = {}
                st.rerun()


def render_progresso():
    st.markdown("## 📊 Meu Progresso")

    engine = get_study_engine()
    stats = engine.get_estatisticas()
    licoes = engine.get_licoes_concluidas()

    # Métricas
    col1, col2, col3 = st.columns(3)
    col1.metric("Lições Concluídas", stats['licoes_concluidas'])
    col2.metric("Questões Respondidas", stats['questoes_respondidas'])
    col3.metric("Taxa de Acerto", f"{stats['taxa_acerto']}%")

    st.markdown("---")

    # Histórico
    st.markdown("### 📜 Histórico de Lições")

    if not licoes:
        st.info("Nenhuma lição concluída ainda. Comece a estudar!")
    else:
        for licao in reversed(licoes):
            taxa = licao.avaliacao.taxa_acerto if licao.avaliacao else 0
            icon = "🌟" if taxa >= 85 else "📗" if taxa >= 70 else "📙"

            with st.expander(f"{icon} {licao.titulo} - {taxa:.0f}%"):
                st.markdown(f"**Capítulo:** {licao.capitulo_ash_sap}")
                st.markdown(f"**Data:** {licao.data_conclusao[:10] if licao.data_conclusao else 'N/A'}")

                if licao.pontos_chave:
                    st.markdown("**Pontos-Chave:**")
                    for p in licao.pontos_chave[:5]:
                        st.markdown(f"• {p}")


def render_importar():
    st.markdown("## 📥 Importar Lição do Claude")
    st.markdown("Cole aqui o JSON de uma lição gerada em conversas anteriores.")

    json_input = st.text_area(
        "Cole o JSON da lição:",
        height=300,
        placeholder='{"licao_id": "...", "titulo": "...", ...}'
    )

    if st.button("📥 Importar", type="primary"):
        try:
            data = json.loads(json_input)

            # Verifica se é uma lição ou lista de lições
            if "licoes_concluidas" in data:
                licoes = data["licoes_concluidas"]
            elif isinstance(data, list):
                licoes = data
            else:
                licoes = [data]

            engine = get_study_engine()
            count = 0
            for licao_data in licoes:
                engine.importar_licao_json(licao_data)
                count += 1

            st.success(f"✅ {count} lição(ões) importada(s) com sucesso!")
            st.rerun()

        except json.JSONDecodeError:
            st.error("❌ JSON inválido. Verifique o formato.")
        except Exception as e:
            st.error(f"❌ Erro: {str(e)}")


# ============================================
# MAIN
# ============================================
def main():
    init_session_state()
    render_sidebar()

    page = st.session_state.page

    if page == "dashboard":
        render_dashboard()
    elif page == "trilhas":
        render_trilhas()
    elif page == "estudar":
        render_estudar()
    elif page == "progresso":
        render_progresso()
    elif page == "importar":
        render_importar()
    else:
        render_dashboard()


if __name__ == "__main__":
    main()

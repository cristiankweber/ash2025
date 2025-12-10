"""
app.py - Interface Streamlit da ASH-SAP Study Platform (Modo Offline)

Funciona 100% offline - apenas importa e navega lições do Claude.
NÃO requer API key.
"""
import streamlit as st
import json
from datetime import datetime

from config import DATA_DIR
from study_engine import get_study_engine
from models import LessonStatus
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
        background: #f8f9fa;
        border: 1px solid #ddd;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    .lesson-card {
        background: white;
        border-left: 4px solid #8B0000;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 0 10px 10px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .points-box {
        background: #fff3cd;
        border: 1px solid #ffc107;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
    }
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
        "viewing_licao_id": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


# ============================================
# SIDEBAR
# ============================================
def render_sidebar():
    st.sidebar.markdown("## 🩸 ASH-SAP Study")
    st.sidebar.markdown("*Modo Offline*")
    st.sidebar.markdown("---")

    # Navegação
    st.sidebar.markdown("### 📍 Navegação")

    if st.sidebar.button("🏠 Dashboard", use_container_width=True):
        st.session_state.page = "dashboard"
        st.rerun()

    if st.sidebar.button("📚 Trilhas", use_container_width=True):
        st.session_state.page = "trilhas"
        st.rerun()

    if st.sidebar.button("📖 Minhas Lições", use_container_width=True):
        st.session_state.page = "licoes"
        st.rerun()

    if st.sidebar.button("📥 Importar JSON", use_container_width=True, type="primary"):
        st.session_state.page = "importar"
        st.rerun()

    if st.sidebar.button("📤 Exportar Progresso", use_container_width=True):
        st.session_state.page = "exportar"
        st.rerun()

    st.sidebar.markdown("---")

    # Estatísticas
    engine = get_study_engine()
    stats = engine.get_estatisticas()

    st.sidebar.markdown("### 📊 Resumo")
    st.sidebar.metric("Lições Importadas", f"{stats['licoes_concluidas']}/{stats['total_licoes']}")
    st.sidebar.progress(stats['percentual'] / 100 if stats['percentual'] > 0 else 0)

    if stats['questoes_respondidas'] > 0:
        st.sidebar.metric("Taxa de Acerto", f"{stats['taxa_acerto']}%")

    st.sidebar.markdown("---")
    st.sidebar.info("💡 **Dica:** Importe suas lições do Claude para começar!")


# ============================================
# PÁGINAS
# ============================================
def render_dashboard():
    st.markdown('<h1 class="main-header">🩸 ASH-SAP Study Platform</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Plataforma de Estudo em Hematologia - Modo Offline</p>', unsafe_allow_html=True)

    engine = get_study_engine()
    stats = engine.get_estatisticas()
    licoes = engine.get_licoes_concluidas()

    # Cards de estatísticas
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-number">{stats['licoes_concluidas']}</div>
            <div>Lições Importadas</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-number">{stats['percentual']}%</div>
            <div>Progresso</div>
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
            <div>Questões</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Ações principais
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📥 Importar Lições")
        st.markdown("""
        Importe lições das suas conversas com o Claude.
        Cole o JSON completo ou lições individuais.
        """)
        if st.button("📥 Ir para Importação", type="primary", use_container_width=True):
            st.session_state.page = "importar"
            st.rerun()

    with col2:
        st.markdown("### 📖 Ver Lições")
        if licoes:
            st.markdown(f"Você tem **{len(licoes)} lições** importadas.")
            if st.button("📖 Ver Minhas Lições", use_container_width=True):
                st.session_state.page = "licoes"
                st.rerun()
        else:
            st.info("Nenhuma lição importada ainda.")

    # Lições recentes
    if licoes:
        st.markdown("---")
        st.markdown("### 📚 Lições Recentes")

        for licao in licoes[-3:]:
            taxa = licao.avaliacao.taxa_acerto if licao.avaliacao else 0
            st.markdown(f"""
            <div class="lesson-card">
                <strong>Cap. {licao.capitulo_ash_sap}: {licao.titulo}</strong><br>
                <small>Taxa de acerto: {taxa:.0f}%</small>
            </div>
            """, unsafe_allow_html=True)


def render_trilhas():
    st.markdown("## 📚 Trilhas de Estudo")
    st.markdown("Veja o progresso em cada trilha do ASH-SAP.")
    st.markdown("---")

    engine = get_study_engine()
    trilhas = engine.get_trilhas()

    for trilha in trilhas:
        caps_concluidos = engine.get_capitulos_concluidos(trilha.id)
        total_caps = len(trilha.capitulos)
        progresso = len(caps_concluidos) / total_caps if total_caps > 0 else 0

        with st.expander(f"**{trilha.nome}** ({len(caps_concluidos)}/{total_caps} capítulos)", expanded=False):
            st.markdown(f"*{trilha.descricao}*")
            st.progress(progresso)

            # Lista de capítulos
            for cap in trilha.capitulos:
                info = CHAPTER_INFO.get(cap, {"titulo": f"Capítulo {cap}"})
                if cap in caps_concluidos:
                    licao = engine.get_licao_by_capitulo(cap)
                    taxa = licao.avaliacao.taxa_acerto if licao and licao.avaliacao else 0
                    st.markdown(f"✅ **Cap. {cap}:** {info['titulo']} ({taxa:.0f}%)")
                else:
                    st.markdown(f"⬜ **Cap. {cap}:** {info['titulo']}")


def render_licoes():
    st.markdown("## 📖 Minhas Lições")
    st.markdown("Lições importadas das suas conversas com o Claude.")
    st.markdown("---")

    engine = get_study_engine()
    licoes = engine.get_licoes_concluidas()

    if not licoes:
        st.info("📭 Nenhuma lição importada ainda.")
        st.markdown("Vá em **📥 Importar JSON** para adicionar suas lições.")
        return

    # Filtro por trilha
    trilhas = engine.get_trilhas()
    trilha_options = ["Todas"] + [t.nome for t in trilhas]
    filtro = st.selectbox("Filtrar por trilha:", trilha_options)

    # Lista de lições
    for licao in reversed(licoes):
        trilha = engine.get_trilha(licao.trilha_id)
        trilha_nome = trilha.nome if trilha else "Desconhecida"

        if filtro != "Todas" and trilha_nome != filtro:
            continue

        taxa = licao.avaliacao.taxa_acerto if licao.avaliacao else 0
        icon = "🌟" if taxa >= 85 else "📗" if taxa >= 70 else "📙"

        with st.expander(f"{icon} **Cap. {licao.capitulo_ash_sap}: {licao.titulo}** - {taxa:.0f}%"):
            st.markdown(f"**Trilha:** {trilha_nome}")
            st.markdown(f"**Data:** {licao.data_conclusao[:10] if licao.data_conclusao else 'N/A'}")

            # Objetivos
            if licao.objetivos_aprendizado:
                st.markdown("**Objetivos de Aprendizado:**")
                for obj in licao.objetivos_aprendizado:
                    st.markdown(f"• {obj}")

            # Tópicos
            if licao.topicos:
                st.markdown("**Tópicos Abordados:**")
                for topico in licao.topicos:
                    st.markdown(f"• **{topico.nome}**")
                    for sub in topico.subtopicos[:3]:
                        st.markdown(f"  - {sub}")

            # Pontos-chave
            if licao.pontos_chave:
                st.markdown("---")
                st.markdown('<div class="points-box">', unsafe_allow_html=True)
                st.markdown("**📌 Pontos-Chave para Memorização:**")
                for ponto in licao.pontos_chave:
                    st.markdown(f"• {ponto}")
                st.markdown('</div>', unsafe_allow_html=True)

            # Resultado do Quiz
            if licao.avaliacao:
                st.markdown("---")
                st.markdown(f"**📝 Quiz:** {licao.avaliacao.questoes_corretas}/{licao.avaliacao.total_questoes} ({licao.avaliacao.taxa_acerto:.0f}%)")


def render_importar():
    st.markdown("## 📥 Importar Lições do Claude")
    st.markdown("""
    Cole aqui o JSON das suas conversas com o Claude.

    **Formatos aceitos:**
    - JSON completo (com `licoes_concluidas`)
    - Lição individual
    - Lista de lições
    """)
    st.markdown("---")

    # Área de texto para o JSON
    json_input = st.text_area(
        "Cole o JSON aqui:",
        height=400,
        placeholder='{\n  "licoes_concluidas": [\n    {\n      "licao_id": "licao_1",\n      "titulo": "...",\n      ...\n    }\n  ]\n}'
    )

    col1, col2 = st.columns(2)

    with col1:
        if st.button("📥 Importar", type="primary", use_container_width=True):
            if not json_input.strip():
                st.error("❌ Cole um JSON válido!")
                return

            try:
                data = json.loads(json_input)
                engine = get_study_engine()

                # Determina o tipo de JSON
                if "licoes_concluidas" in data:
                    # JSON completo
                    count = engine.importar_json_completo(data)
                    st.success(f"✅ {count} lição(ões) importada(s)!")
                elif isinstance(data, list):
                    # Lista de lições
                    count = 0
                    for item in data:
                        engine.importar_licao_json(item)
                        count += 1
                    st.success(f"✅ {count} lição(ões) importada(s)!")
                else:
                    # Lição individual
                    engine.importar_licao_json(data)
                    st.success("✅ Lição importada!")

                st.balloons()
                st.rerun()

            except json.JSONDecodeError as e:
                st.error(f"❌ JSON inválido: {e}")
            except Exception as e:
                st.error(f"❌ Erro: {e}")

    with col2:
        if st.button("🗑️ Limpar", use_container_width=True):
            st.rerun()

    # Exemplo de formato
    with st.expander("📋 Ver exemplo de formato JSON"):
        st.code('''
{
  "licoes_concluidas": [
    {
      "licao_id": "licao_1",
      "trilha": "Trilha 9 - Hematologia Consultiva",
      "capitulo_ash_sap": 1,
      "titulo": "Manejo Perioperatório em Hematologia",
      "objetivos_aprendizado": [
        "Objetivo 1",
        "Objetivo 2"
      ],
      "topicos_abordados": [
        {
          "topico": "Nome do Tópico",
          "subtopicos": ["Sub1", "Sub2"]
        }
      ],
      "pontos_chave_memorizacao": [
        "Ponto importante 1",
        "Ponto importante 2"
      ],
      "avaliacao": {
        "total_questoes": 7,
        "questoes_corretas": 5,
        "taxa_acerto": 71.4,
        "questoes": [
          {
            "numero": 1,
            "tema": "Tema da questão",
            "resposta_aluno": "A",
            "resposta_correta": "D",
            "resultado": "incorreta",
            "conceito_chave": "Conceito avaliado"
          }
        ]
      },
      "data_conclusao": "2025-12-10"
    }
  ]
}
        ''', language="json")


def render_exportar():
    st.markdown("## 📤 Exportar Progresso")
    st.markdown("Exporte seu progresso para backup ou transferência.")
    st.markdown("---")

    engine = get_study_engine()
    data = engine.exportar_progresso()

    json_str = json.dumps(data, ensure_ascii=False, indent=2)

    st.text_area("JSON do Progresso:", json_str, height=400)

    st.download_button(
        label="📥 Baixar JSON",
        data=json_str,
        file_name="ash_sap_progresso.json",
        mime="application/json"
    )


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
    elif page == "licoes":
        render_licoes()
    elif page == "importar":
        render_importar()
    elif page == "exportar":
        render_exportar()
    else:
        render_dashboard()


if __name__ == "__main__":
    main()

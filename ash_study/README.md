# 🩸 ASH-SAP Study Platform

Plataforma adaptativa de estudo em Hematologia baseada no ASH-SAP 9th Edition (2025).

## Funcionalidades

- **9 Trilhas de Aprendizado** organizadas por tema
- **Geração de Lições** via Claude AI
- **Quiz Interativo** com correção automática
- **Acompanhamento de Progresso** completo
- **Importação de Lições** de conversas anteriores
- **Sistema de Revisão Espaçada**

## Trilhas Disponíveis

1. Hemostasia e Trombose
2. Anemias
3. Hemoglobinopatias
4. Plaquetas e Distúrbios Plaquetários
5. Neoplasias Mieloides
6. Neoplasias Linfoides
7. Transplante e Terapia Celular
8. Medicina Transfusional
9. Hematologia Consultiva e Especial

## Instalação

```bash
# Clone o repositório
git clone <repo-url>
cd ash_study

# Instale as dependências
pip install -r requirements.txt

# Configure a API key
cp .env.example .env
# Edite .env com sua ANTHROPIC_API_KEY

# Execute
streamlit run app.py
```

## Uso

1. **Dashboard**: Visão geral do progresso
2. **Trilhas**: Navegue pelas trilhas e selecione capítulos
3. **Estudar**: Gere lições e faça quizzes
4. **Progresso**: Acompanhe seu histórico
5. **Importar**: Importe lições de conversas anteriores

## Importar Lições Anteriores

Se você já estudou com o Claude, pode importar suas lições:

1. Vá em "📥 Importar Lição"
2. Cole o JSON da lição (formato do HemaTutor)
3. Clique em "Importar"

## Requisitos

- Python 3.9+
- Anthropic API Key

## Licença

Projeto educacional.

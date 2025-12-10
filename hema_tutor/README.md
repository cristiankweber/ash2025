# 🩸 HemaTutor

**Plataforma Adaptativa de Ensino em Hematologia**

HemaTutor é um MVP de plataforma educacional baseada em RAG (Retrieval-Augmented Generation) que utiliza o conteúdo do ASH-SAP (American Society of Hematology Self-Assessment Program) para criar experiências de aprendizado personalizadas em Hematologia.

## 🚀 Funcionalidades

- **📄 Processamento de PDF**: Upload e indexação automática do material ASH-SAP
- **🛤️ Trilhas de Aprendizado**: Organização do conteúdo em temas (Anemias, Hemostasia, Neoplasias, etc.)
- **📚 Lições Estruturadas**: Geração de lições com teoria, aplicação clínica e pontos-chave
- **📝 Quiz Interativo**: Questões de múltipla escolha com correção e explicações
- **📊 Dashboard de Progresso**: Acompanhamento de lições concluídas e score de acertos
- **❓ Perguntas Livres**: Chat com o Professor HemaTutor baseado no material

## 🛠️ Stack Tecnológico

| Componente | Tecnologia |
|------------|------------|
| Interface | Streamlit |
| LLM Orchestration | LangChain |
| Vector Store | FAISS / ChromaDB |
| Modelos | OpenAI GPT-4o / Claude 3.5 Sonnet |
| Embeddings | OpenAI text-embedding-3-small |
| PDF Processing | PyPDF |

## 📁 Estrutura do Projeto

```
hema_tutor/
├── app.py              # Interface Streamlit (UI principal)
├── rag_engine.py       # Motor de RAG (ingestão, busca, geração)
├── prompts.py          # System prompts e templates
├── config.py           # Configurações e variáveis de ambiente
├── data/
│   ├── uploads/        # PDFs enviados pelos usuários
│   └── vectorstores/   # Índices vetoriais persistidos
├── requirements.txt    # Dependências do projeto
├── .env.example        # Template de variáveis de ambiente
└── README.md           # Este arquivo
```

## 🔧 Instalação

### 1. Clone o repositório

```bash
git clone <repository-url>
cd hema_tutor
```

### 2. Crie um ambiente virtual

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Configure as variáveis de ambiente

```bash
cp .env.example .env
# Edite o arquivo .env com suas chaves de API
```

### 5. Execute a aplicação

```bash
streamlit run app.py
```

A aplicação estará disponível em `http://localhost:8501`

## ⚙️ Configuração

### Variáveis de Ambiente (.env)

```env
# === LLM Configuration ===
LLM_PROVIDER=openai              # "openai" ou "anthropic"
OPENAI_API_KEY=sk-xxx            # Obrigatório (também para embeddings)
ANTHROPIC_API_KEY=sk-ant-xxx     # Necessário se LLM_PROVIDER=anthropic

# === Model Settings ===
OPENAI_MODEL=gpt-4o
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022
LLM_TEMPERATURE=0.3
LLM_MAX_TOKENS=4096

# === VectorStore ===
VECTORSTORE_TYPE=faiss           # "faiss" ou "chroma"
EMBEDDING_MODEL=text-embedding-3-small

# === Chunking ===
CHUNK_SIZE=1200
CHUNK_OVERLAP=250
RETRIEVER_K=6
```

## 📖 Como Usar

1. **Upload do Material**: Na barra lateral, faça upload do PDF do ASH-SAP
2. **Processamento**: Clique em "Processar Material" e aguarde a indexação
3. **Escolha uma Trilha**: Selecione um tema de estudo no dropdown
4. **Estude a Lição**: Leia o conteúdo teórico e aplicações clínicas
5. **Teste seu Conhecimento**: Complete o quiz e veja seu desempenho
6. **Acompanhe o Progresso**: Visualize seu score e histórico na sidebar

## 🔒 Princípios de Segurança

O HemaTutor foi desenvolvido com foco em **segurança de informação médica**:

- ✅ Respostas **exclusivamente** baseadas no material fornecido
- ✅ Nunca inventa dados, doses ou diretrizes
- ✅ Transparência sobre limitações do conhecimento
- ✅ Avisos de que o conteúdo é apenas educacional

## 🤝 Contribuição

Contribuições são bem-vindas! Por favor, abra uma issue ou pull request.

## 📄 Licença

Este projeto é para fins educacionais.

---

**Desenvolvido com ❤️ para a comunidade médica**

"""
prompts.py - System Prompts e Templates do HemaTutor

Este módulo define a "personalidade" da IA como Professor de Hematologia,
contendo:
- System prompt principal do Professor Especialista
- Template para geração de lições estruturadas
- Template para geração de quiz
- Instruções de RAG para manter fidelidade ao conteúdo do PDF
"""

# ============================================
# SYSTEM PROMPT - PROFESSOR DE HEMATOLOGIA
# ============================================
SYSTEM_PROMPT_PROFESSOR = """Você é o **Professor HemaTutor**, um especialista em Hematologia com décadas de experiência clínica e acadêmica. Sua missão é ensinar conceitos de hematologia de forma clara, didática e clinicamente relevante.

## PERSONALIDADE E ESTILO:
- Seja acolhedor e encorajador, como um mentor dedicado
- Use linguagem técnica precisa, mas explique termos complexos
- Conecte sempre a teoria com a prática clínica
- Utilize analogias e exemplos para facilitar a compreensão
- Mantenha um tom profissional, porém acessível

## REGRAS FUNDAMENTAIS DE RAG (RETRIEVAL-AUGMENTED GENERATION):

### 1. FIDELIDADE AO CONTEÚDO:
- Responda **EXCLUSIVAMENTE** com base no contexto fornecido pelo PDF ASH-SAP
- **NUNCA** invente informações, diretrizes, doses de medicamentos ou estudos clínicos
- **NUNCA** cite referências bibliográficas que não estejam explicitamente no contexto
- Se o contexto não trouxer informação suficiente, diga claramente: "Com base no material disponível, não tenho informações suficientes sobre este tópico específico."

### 2. TRANSPARÊNCIA:
- Quando citar dados numéricos (doses, percentuais, valores de referência), indique que vêm do material de estudo
- Se houver ambiguidade no contexto, apresente as diferentes interpretações possíveis
- Não extrapole além do que está escrito no material

### 3. SEGURANÇA CLÍNICA:
- Lembre sempre que as informações são para fins educacionais
- Não forneça recomendações de tratamento individualizadas
- Enfatize a importância de consultar protocolos institucionais e guidelines atualizados

## FORMATO DAS RESPOSTAS:
- Use markdown para estruturar suas respostas
- Utilize bullet points para listas
- Destaque termos importantes em **negrito**
- Separe seções com cabeçalhos claros
"""

# ============================================
# TEMPLATE DE LIÇÃO ESTRUTURADA
# ============================================
LESSON_TEMPLATE = """## TAREFA:
Gere uma **LIÇÃO EDUCACIONAL** sobre o tema "{track}" com base EXCLUSIVAMENTE no contexto fornecido abaixo.

## CONTEXTO DO MATERIAL ASH-SAP:
{context}

## ESTRUTURA OBRIGATÓRIA DA LIÇÃO:

### 📚 CONCEITO TEÓRICO
Explique os fundamentos teóricos do tema, incluindo:
- Definições essenciais
- Fisiopatologia relevante
- Classificações importantes
- Mecanismos envolvidos

### 🏥 APLICAÇÃO CLÍNICA
Conecte a teoria com a prática médica:
- Manifestações clínicas típicas
- Abordagem diagnóstica
- Princípios de tratamento (sem doses específicas se não estiverem no contexto)
- Pontos de atenção para a prática

### 📝 PONTOS-CHAVE
Liste 3-5 pontos essenciais que o estudante deve memorizar.

## REGRAS:
1. Use APENAS informações presentes no contexto fornecido
2. Se alguma seção não puder ser completada com o contexto, indique "Informação não disponível no material consultado"
3. Mantenha linguagem didática e acessível
4. Extensão ideal: 400-600 palavras no total
"""

# ============================================
# TEMPLATE DE QUIZ
# ============================================
QUIZ_TEMPLATE = """## TAREFA:
Com base na lição gerada e no contexto do material ASH-SAP, crie **{num_questions} questões de múltipla escolha** para avaliar a compreensão do estudante.

## CONTEXTO DO MATERIAL:
{context}

## LIÇÃO APRESENTADA:
{lesson_content}

## FORMATO OBRIGATÓRIO DAS QUESTÕES:

Para cada questão, siga EXATAMENTE este formato JSON:

```json
{{
  "questions": [
    {{
      "id": 1,
      "question": "Texto da pergunta aqui?",
      "options": {{
        "A": "Alternativa A",
        "B": "Alternativa B",
        "C": "Alternativa C",
        "D": "Alternativa D"
      }},
      "correct_answer": "A",
      "explanation": "Explicação detalhada de por que A é a resposta correta e por que as outras estão erradas."
    }},
    {{
      "id": 2,
      ...
    }}
  ]
}}
```

## REGRAS PARA AS QUESTÕES:
1. **Todas as questões devem ser baseadas EXCLUSIVAMENTE no contexto e na lição fornecidos**
2. Crie questões que testem compreensão, não apenas memorização
3. As alternativas incorretas devem ser plausíveis (distratores de qualidade)
4. A explicação deve ser educativa e reforçar o aprendizado
5. Varie o nível de dificuldade (1 fácil, 1 média, 1 difícil)
6. Evite questões com "todas as anteriores" ou "nenhuma das anteriores"
7. As alternativas devem ter tamanho similar
8. Retorne APENAS o JSON, sem texto adicional antes ou depois
"""

# ============================================
# TEMPLATE PARA EXTRAÇÃO DE TRILHAS
# ============================================
TRACK_EXTRACTION_TEMPLATE = """## TAREFA:
Analise o índice/sumário do documento ASH-SAP fornecido abaixo e identifique as principais **TRILHAS DE APRENDIZADO** em Hematologia.

## CONTEÚDO DO ÍNDICE/PRIMEIRAS PÁGINAS:
{toc_content}

## INSTRUÇÕES:
1. Identifique os grandes temas/capítulos do material
2. Agrupe tópicos relacionados em trilhas coerentes
3. Nomeie cada trilha de forma clara e concisa
4. Retorne no formato JSON abaixo

## FORMATO DE SAÍDA:
```json
{{
  "tracks": [
    {{
      "name": "Nome da Trilha",
      "description": "Breve descrição do que será abordado",
      "chapters": ["Capítulo 1", "Capítulo 2"],
      "keywords": ["palavra-chave1", "palavra-chave2"]
    }}
  ]
}}
```

## TRILHAS ESPERADAS (use como referência, mas adapte ao conteúdo real):
- Anemias (ferropriva, megaloblástica, hemolítica, aplástica)
- Hemostasia e Trombose (coagulação, anticoagulantes, trombofilia)
- Neoplasias Hematológicas (leucemias, linfomas, mieloma)
- Transplante de Medula Óssea / Células-Tronco
- Hemoglobinopatias (anemia falciforme, talassemias)
- Distúrbios Leucocitários
- Medicina Transfusional

Retorne APENAS o JSON, sem texto adicional.
"""

# ============================================
# TEMPLATE PARA IDENTIFICAR CAPÍTULO DO CHUNK
# ============================================
CHAPTER_IDENTIFICATION_TEMPLATE = """Analise o texto abaixo e identifique:
1. O capítulo/seção a que pertence
2. A trilha de aprendizado mais adequada

Texto:
{chunk_text}

Trilhas disponíveis: {available_tracks}

Responda no formato JSON:
```json
{{
  "chapter": "Nome do Capítulo",
  "track": "Nome da Trilha",
  "page_hint": "número da página se identificável, ou null"
}}
```
"""

# ============================================
# PROMPT PARA CHAT LIVRE (Q&A)
# ============================================
QA_PROMPT = """## CONTEXTO DO MATERIAL ASH-SAP:
{context}

## PERGUNTA DO ESTUDANTE:
{question}

## INSTRUÇÕES:
1. Responda APENAS com base no contexto fornecido acima
2. Se a resposta não estiver no contexto, diga claramente que não possui essa informação no material disponível
3. Seja didático e use exemplos quando apropriado
4. Estruture a resposta de forma clara com markdown
5. Se for uma pergunta sobre doses ou tratamentos, lembre que as informações são para fins educacionais
"""

# ============================================
# MENSAGENS DE FEEDBACK
# ============================================
FEEDBACK_MESSAGES = {
    "correct": [
        "🎉 **Excelente!** Resposta correta!",
        "✅ **Muito bem!** Você acertou!",
        "🌟 **Perfeito!** Continue assim!",
        "💪 **Correto!** Ótimo conhecimento!",
    ],
    "incorrect": [
        "❌ **Não foi dessa vez.** Veja a explicação abaixo.",
        "📚 **Resposta incorreta.** Aproveite para revisar.",
        "🔄 **Errou, mas faz parte!** Veja o porquê abaixo.",
    ],
    "encouragement": [
        "Continue estudando! Cada erro é uma oportunidade de aprendizado.",
        "A hematologia é complexa, mas você está progredindo!",
        "Não desanime! A prática leva à excelência.",
    ],
}

# ============================================
# FUNÇÕES AUXILIARES
# ============================================

def get_lesson_prompt(track: str, context: str) -> str:
    """
    Gera o prompt completo para criação de uma lição.

    Args:
        track: Nome da trilha de aprendizado
        context: Contexto recuperado do VectorStore

    Returns:
        str: Prompt formatado para o LLM
    """
    return LESSON_TEMPLATE.format(track=track, context=context)


def get_quiz_prompt(context: str, lesson_content: str, num_questions: int = 3) -> str:
    """
    Gera o prompt completo para criação do quiz.

    Args:
        context: Contexto recuperado do VectorStore
        lesson_content: Conteúdo da lição gerada
        num_questions: Número de questões a gerar

    Returns:
        str: Prompt formatado para o LLM
    """
    return QUIZ_TEMPLATE.format(
        context=context,
        lesson_content=lesson_content,
        num_questions=num_questions
    )


def get_qa_prompt(context: str, question: str) -> str:
    """
    Gera o prompt para perguntas livres.

    Args:
        context: Contexto recuperado do VectorStore
        question: Pergunta do usuário

    Returns:
        str: Prompt formatado para o LLM
    """
    return QA_PROMPT.format(context=context, question=question)


def get_track_extraction_prompt(toc_content: str) -> str:
    """
    Gera o prompt para extração de trilhas do índice.

    Args:
        toc_content: Conteúdo do índice/primeiras páginas

    Returns:
        str: Prompt formatado para o LLM
    """
    return TRACK_EXTRACTION_TEMPLATE.format(toc_content=toc_content)


import random

def get_feedback_message(is_correct: bool) -> str:
    """
    Retorna uma mensagem de feedback aleatória.

    Args:
        is_correct: Se a resposta foi correta

    Returns:
        str: Mensagem de feedback
    """
    key = "correct" if is_correct else "incorrect"
    return random.choice(FEEDBACK_MESSAGES[key])


def get_encouragement_message() -> str:
    """
    Retorna uma mensagem de encorajamento.

    Returns:
        str: Mensagem de encorajamento
    """
    return random.choice(FEEDBACK_MESSAGES["encouragement"])

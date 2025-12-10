"""
prompts.py - Prompts para geração de conteúdo educacional ASH-SAP
"""

SYSTEM_PROMPT = """Você é o **Professor ASH-SAP**, um especialista em Hematologia com vasta experiência clínica e acadêmica. Sua missão é conduzir um curso estruturado baseado no ASH-SAP 9th Edition (2025).

## PERFIL DO ALUNO
- Médico Hematologista e Especialista em TMO
- Nível: Avançado
- Objetivo: Revisão estruturada e aprofundamento em Hematologia

## ESTILO PEDAGÓGICO
1. **Didático e Objetivo**: Vá direto ao ponto, mas seja completo
2. **Clinicamente Relevante**: Sempre conecte teoria à prática médica
3. **Baseado em Evidências**: Cite estudos e guidelines quando apropriado
4. **Estruturado**: Use formatação clara com seções, bullets e tabelas

## REGRAS FUNDAMENTAIS
- Baseie-se EXCLUSIVAMENTE no conteúdo do ASH-SAP 9th Edition
- NÃO invente dados, doses, estudos ou diretrizes
- Se não souber algo, diga explicitamente
- Use português brasileiro formal médico
- Formate com Markdown para melhor leitura
"""

LESSON_GENERATION_PROMPT = """## TAREFA
Gere uma **LIÇÃO COMPLETA** sobre o Capítulo {capitulo} do ASH-SAP: "{titulo}"

## ESTRUTURA OBRIGATÓRIA

### 1. CABEÇALHO
- Título da lição
- Capítulo ASH-SAP de referência
- Tempo estimado de estudo
- Nível de dificuldade

### 2. OBJETIVOS DE APRENDIZADO
Liste 4-6 objetivos específicos e mensuráveis.

### 3. CONTEÚDO PRINCIPAL
Organize em tópicos e subtópicos:

#### 3.1 Conceitos Fundamentais
- Definições essenciais
- Fisiopatologia
- Classificações

#### 3.2 Abordagem Diagnóstica
- Sinais e sintomas
- Exames laboratoriais
- Diagnóstico diferencial

#### 3.3 Manejo Clínico
- Indicações de tratamento
- Opções terapêuticas (sem doses específicas a menos que sejam padrão universal)
- Monitoramento

#### 3.4 Situações Especiais
- Casos complexos
- Populações específicas
- Controvérsias atuais

### 4. PONTOS-CHAVE PARA MEMORIZAÇÃO
Liste 8-12 pontos essenciais em formato de bullets concisos.

### 5. APLICAÇÃO CLÍNICA
Um ou dois cenários clínicos breves mostrando aplicação prática.

## FORMATAÇÃO
- Use **negrito** para termos importantes
- Use tabelas quando apropriado
- Use listas para facilitar memorização
- Extensão: 1500-2500 palavras
"""

QUIZ_GENERATION_PROMPT = """## TAREFA
Gere {num_questoes} questões de múltipla escolha baseadas na lição sobre "{titulo}".

## CONTEÚDO DA LIÇÃO PARA REFERÊNCIA:
{conteudo_licao}

## FORMATO OBRIGATÓRIO (JSON)
Retorne APENAS o JSON abaixo, sem texto adicional:

```json
{{
  "questoes": [
    {{
      "numero": 1,
      "tema": "Tema específico da questão",
      "cenario": "Descrição do caso clínico ou situação (2-4 linhas)",
      "pergunta": "A pergunta objetiva",
      "opcoes": {{
        "A": "Alternativa A",
        "B": "Alternativa B",
        "C": "Alternativa C",
        "D": "Alternativa D",
        "E": "Alternativa E"
      }},
      "resposta_correta": "A",
      "explicacao": "Explicação detalhada de por que A é correta e as outras são incorretas",
      "conceito_chave": "O conceito principal que a questão avalia"
    }}
  ]
}}
```

## REGRAS PARA AS QUESTÕES
1. Varie os níveis: 2 fáceis, 2 médias, 1 difícil
2. Use cenários clínicos realistas
3. Alternativas incorretas devem ser distratores plausíveis
4. A explicação deve ser educativa
5. Evite "todas as anteriores" ou "nenhuma das anteriores"
6. Cada questão deve testar um conceito diferente
"""

FEEDBACK_PROMPT = """## TAREFA
Analise o desempenho do aluno nas questões e forneça feedback educativo.

## RESULTADO DO QUIZ
- Total de questões: {total}
- Acertos: {corretas}
- Taxa de acerto: {taxa}%

## RESPOSTAS DO ALUNO
{respostas_detalhadas}

## FORNEÇA

### 1. ANÁLISE GERAL
Comentário sobre o desempenho geral.

### 2. PONTOS FORTES
Liste 2-4 áreas que o aluno demonstrou domínio.

### 3. ÁREAS PARA REFORÇO
Para cada erro, indique:
- O tópico específico
- Por que a resposta estava incorreta
- Recomendação de revisão

### 4. PRÓXIMOS PASSOS
Recomendação sobre avançar ou revisar.

Seja encorajador mas honesto.
"""

CHAPTER_INFO = {
    1: {"titulo": "Perioperative Hematology", "autores": ["Jordan Schaefer", "Geoffrey Barnes"]},
    2: {"titulo": "Outpatient Hematology", "autores": ["Various"]},
    3: {"titulo": "Consultative Hematology", "autores": ["Various"]},
    4: {"titulo": "Hematology in Pregnancy", "autores": ["Various"]},
    5: {"titulo": "Pediatric Hematology", "autores": ["Various"]},
    6: {"titulo": "Approach to Anemia", "autores": ["Various"]},
    7: {"titulo": "Iron Deficiency Anemia", "autores": ["Various"]},
    8: {"titulo": "Megaloblastic Anemia", "autores": ["Various"]},
    9: {"titulo": "Acquired Hemolytic Anemia", "autores": ["Various"]},
    10: {"titulo": "Sickle Cell Disease", "autores": ["Various"]},
    11: {"titulo": "Thalassemia Syndromes", "autores": ["Various"]},
    12: {"titulo": "Bone Marrow Failure Syndromes", "autores": ["Various"]},
    13: {"titulo": "Aplastic Anemia", "autores": ["Various"]},
    14: {"titulo": "Pure Red Cell Aplasia", "autores": ["Various"]},
    15: {"titulo": "Overview of Hemostasis", "autores": ["Various"]},
    16: {"titulo": "Laboratory Evaluation of Hemostasis", "autores": ["Various"]},
    17: {"titulo": "Bleeding Disorders", "autores": ["Various"]},
    18: {"titulo": "Hemophilia", "autores": ["Various"]},
    19: {"titulo": "Von Willebrand Disease", "autores": ["Various"]},
    20: {"titulo": "Venous Thromboembolism", "autores": ["Various"]},
    21: {"titulo": "Anticoagulation Therapy", "autores": ["Various"]},
    22: {"titulo": "Thrombophilia", "autores": ["Various"]},
    23: {"titulo": "Platelet Disorders Overview", "autores": ["Various"]},
    24: {"titulo": "Immune Thrombocytopenia", "autores": ["Various"]},
    25: {"titulo": "Thrombotic Microangiopathies", "autores": ["Various"]},
    26: {"titulo": "Heparin-Induced Thrombocytopenia", "autores": ["Various"]},
    27: {"titulo": "Transfusion Medicine Basics", "autores": ["Various"]},
    28: {"titulo": "Blood Components", "autores": ["Various"]},
    29: {"titulo": "Transfusion Reactions", "autores": ["Various"]},
    30: {"titulo": "Hematopoietic Stem Cell Transplantation Overview", "autores": ["Various"]},
    31: {"titulo": "Autologous Transplantation", "autores": ["Various"]},
    32: {"titulo": "Allogeneic Transplantation", "autores": ["Various"]},
    33: {"titulo": "Complications of Transplantation", "autores": ["Various"]},
    34: {"titulo": "Myelodysplastic Syndromes", "autores": ["Various"]},
    35: {"titulo": "Anemia of Chronic Disease", "autores": ["Various"]},
    36: {"titulo": "Myeloproliferative Neoplasms", "autores": ["Various"]},
    37: {"titulo": "Polycythemia Vera", "autores": ["Various"]},
    38: {"titulo": "Essential Thrombocythemia", "autores": ["Various"]},
    39: {"titulo": "Myelofibrosis", "autores": ["Various"]},
    40: {"titulo": "Chronic Myeloid Leukemia", "autores": ["Various"]},
    41: {"titulo": "Acute Myeloid Leukemia", "autores": ["Various"]},
    42: {"titulo": "Acute Lymphoblastic Leukemia", "autores": ["Various"]},
    43: {"titulo": "Chronic Lymphocytic Leukemia", "autores": ["Various"]},
    44: {"titulo": "Hodgkin Lymphoma", "autores": ["Various"]},
    45: {"titulo": "Non-Hodgkin Lymphoma Overview", "autores": ["Various"]},
    46: {"titulo": "Aggressive Lymphomas", "autores": ["Various"]},
    47: {"titulo": "Indolent Lymphomas", "autores": ["Various"]},
    48: {"titulo": "Plasma Cell Neoplasms", "autores": ["Various"]},
    49: {"titulo": "Multiple Myeloma", "autores": ["Various"]},
}


def get_lesson_prompt(capitulo: int) -> str:
    """Gera prompt para criar lição de um capítulo."""
    info = CHAPTER_INFO.get(capitulo, {"titulo": f"Capítulo {capitulo}", "autores": []})
    return LESSON_GENERATION_PROMPT.format(
        capitulo=capitulo,
        titulo=info["titulo"]
    )


def get_quiz_prompt(titulo: str, conteudo: str, num_questoes: int = 5) -> str:
    """Gera prompt para criar quiz."""
    return QUIZ_GENERATION_PROMPT.format(
        titulo=titulo,
        conteudo_licao=conteudo,
        num_questoes=num_questoes
    )


def get_feedback_prompt(total: int, corretas: int, respostas: str) -> str:
    """Gera prompt para feedback."""
    taxa = round((corretas / total) * 100, 1) if total > 0 else 0
    return FEEDBACK_PROMPT.format(
        total=total,
        corretas=corretas,
        taxa=taxa,
        respostas_detalhadas=respostas
    )

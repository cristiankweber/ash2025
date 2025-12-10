"""
study_engine.py - Motor de estudo e geração de conteúdo
"""
import json
import re
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Tuple
from pathlib import Path

import anthropic

from config import (
    ANTHROPIC_API_KEY, MODEL, TEMPERATURE, MAX_TOKENS,
    DATA_DIR, PROGRESS_FILE, LESSONS_FILE,
    QUESTIONS_PER_LESSON, PASSING_SCORE, REVIEW_INTERVAL_DAYS
)
from models import (
    CursoASHSAP, Trilha, Modulo, Licao, Question, Avaliacao,
    ProgressoAluno, LessonStatus, AnaliseDesempenho, Topico
)
from prompts import (
    SYSTEM_PROMPT, get_lesson_prompt, get_quiz_prompt,
    get_feedback_prompt, CHAPTER_INFO
)


class StudyEngine:
    """Motor principal de estudo e geração de conteúdo."""

    def __init__(self):
        self.client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        self.curso: Optional[CursoASHSAP] = None
        self._load_or_create_curso()

    def _load_or_create_curso(self):
        """Carrega curso existente ou cria novo."""
        progress_file = DATA_DIR / "curso_estado.json"
        if progress_file.exists():
            try:
                self.curso = CursoASHSAP.load(str(progress_file))
            except Exception as e:
                print(f"Erro ao carregar curso: {e}")
                self._create_default_curso()
        else:
            self._create_default_curso()

    def _create_default_curso(self):
        """Cria estrutura padrão do curso."""
        self.curso = CursoASHSAP()

        # Define as trilhas baseadas na estrutura do JSON do usuário
        trilhas_config = [
            {
                "id": "trilha_1",
                "nome": "Hemostasia e Trombose",
                "capitulos": [15, 16, 17, 18, 19, 20, 21, 22],
                "ordem": 1
            },
            {
                "id": "trilha_2",
                "nome": "Anemias",
                "capitulos": [6, 7, 8, 9, 12, 13, 14, 35, 39],
                "ordem": 2
            },
            {
                "id": "trilha_3",
                "nome": "Hemoglobinopatias",
                "capitulos": [10, 11],
                "ordem": 3
            },
            {
                "id": "trilha_4",
                "nome": "Plaquetas e Distúrbios Plaquetários",
                "capitulos": [23, 24, 25, 26],
                "ordem": 4
            },
            {
                "id": "trilha_5",
                "nome": "Neoplasias Mieloides",
                "capitulos": [34, 36, 37, 38, 40, 41],
                "ordem": 5
            },
            {
                "id": "trilha_6",
                "nome": "Neoplasias Linfoides",
                "capitulos": [42, 43, 44, 45, 46, 47, 48, 49],
                "ordem": 6
            },
            {
                "id": "trilha_7",
                "nome": "Transplante e Terapia Celular",
                "capitulos": [30, 31, 32, 33],
                "ordem": 7
            },
            {
                "id": "trilha_8",
                "nome": "Medicina Transfusional",
                "capitulos": [27, 28, 29],
                "ordem": 8
            },
            {
                "id": "trilha_9",
                "nome": "Hematologia Consultiva e Especial",
                "capitulos": [1, 2, 3, 4, 5],
                "ordem": 9
            },
        ]

        for t_config in trilhas_config:
            trilha = Trilha(
                id=t_config["id"],
                nome=t_config["nome"],
                capitulos=t_config["capitulos"],
                ordem=t_config["ordem"]
            )
            self.curso.trilhas.append(trilha)

        # Calcula total de lições
        self.curso.progresso.total_licoes = sum(len(t.capitulos) for t in self.curso.trilhas)

        self._save_curso()

    def _save_curso(self):
        """Salva estado do curso."""
        if self.curso:
            self.curso.save(str(DATA_DIR / "curso_estado.json"))

    def _call_claude(self, prompt: str) -> str:
        """Chama a API do Claude."""
        message = self.client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            temperature=TEMPERATURE,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}]
        )
        return message.content[0].text

    def get_trilhas(self) -> List[Trilha]:
        """Retorna lista de trilhas."""
        return sorted(self.curso.trilhas, key=lambda t: t.ordem)

    def get_trilha(self, trilha_id: str) -> Optional[Trilha]:
        """Retorna uma trilha pelo ID."""
        return self.curso.get_trilha(trilha_id)

    def get_progresso(self) -> ProgressoAluno:
        """Retorna progresso do aluno."""
        return self.curso.progresso

    def get_licoes_concluidas(self) -> List[Licao]:
        """Retorna lições concluídas."""
        return self.curso.licoes_concluidas

    def get_capitulos_concluidos(self, trilha_id: str) -> List[int]:
        """Retorna capítulos já concluídos de uma trilha."""
        return [l.capitulo_ash_sap for l in self.curso.licoes_concluidas if l.trilha_id == trilha_id]

    def gerar_licao(self, trilha_id: str, capitulo: int) -> Licao:
        """Gera uma nova lição para um capítulo."""
        # Informações do capítulo
        info = CHAPTER_INFO.get(capitulo, {"titulo": f"Capítulo {capitulo}", "autores": []})

        # Gera conteúdo via Claude
        prompt = get_lesson_prompt(capitulo)
        conteudo = self._call_claude(prompt)

        # Cria objeto da lição
        licao = Licao(
            id=f"licao_{trilha_id}_{capitulo}",
            trilha_id=trilha_id,
            modulo_id=f"modulo_{trilha_id}",
            capitulo_ash_sap=capitulo,
            titulo=info["titulo"],
            autores=info.get("autores", []),
            conteudo=conteudo,
            status=LessonStatus.EM_PROGRESSO,
            data_inicio=datetime.now().isoformat()
        )

        # Atualiza progresso
        self.curso.progresso.trilha_atual = trilha_id
        self.curso.progresso.licao_atual = licao.id
        self.curso.progresso.ultimo_acesso = datetime.now().isoformat()

        self._save_curso()
        return licao

    def gerar_quiz(self, licao: Licao) -> List[Question]:
        """Gera quiz para uma lição."""
        prompt = get_quiz_prompt(
            titulo=licao.titulo,
            conteudo=licao.conteudo,
            num_questoes=QUESTIONS_PER_LESSON
        )

        response = self._call_claude(prompt)

        # Parse do JSON
        questions = []
        try:
            # Extrai JSON da resposta
            json_match = re.search(r'\{[\s\S]*"questoes"[\s\S]*\}', response)
            if json_match:
                data = json.loads(json_match.group())
                for q in data.get("questoes", []):
                    question = Question(
                        numero=q.get("numero", len(questions) + 1),
                        tema=q.get("tema", ""),
                        cenario=q.get("cenario", ""),
                        opcoes=q.get("opcoes", {}),
                        resposta_correta=q.get("resposta_correta", "A"),
                        explicacao=q.get("explicacao", ""),
                        conceito_chave=q.get("conceito_chave", "")
                    )
                    questions.append(question)
        except Exception as e:
            print(f"Erro ao parsear quiz: {e}")
            # Cria questão placeholder
            questions.append(Question(
                numero=1,
                tema="Erro",
                cenario="Houve um erro ao gerar as questões.",
                opcoes={"A": "Tentar novamente"},
                resposta_correta="A",
                explicacao="Por favor, tente gerar o quiz novamente."
            ))

        return questions

    def avaliar_quiz(self, licao: Licao, questoes: List[Question], respostas: Dict[int, str]) -> Avaliacao:
        """Avalia as respostas do quiz."""
        total = len(questoes)
        corretas = 0

        for q in questoes:
            q.resposta_aluno = respostas.get(q.numero)
            if q.resposta_aluno == q.resposta_correta:
                q.resultado = "correta"
                corretas += 1
            else:
                q.resultado = "incorreta"

        taxa = (corretas / total) * 100 if total > 0 else 0

        # Determina status
        if taxa >= 85:
            status = "excelente"
        elif taxa >= 70:
            status = "bom_com_revisao"
        else:
            status = "revisao_necessaria"

        avaliacao = Avaliacao(
            total_questoes=total,
            questoes_corretas=corretas,
            taxa_acerto=taxa,
            status=status,
            questoes=questoes,
            data=datetime.now().isoformat()
        )

        # Atualiza lição
        licao.avaliacao = avaliacao

        return avaliacao

    def concluir_licao(self, licao: Licao) -> None:
        """Marca uma lição como concluída e atualiza progresso."""
        licao.status = LessonStatus.CONCLUIDA
        licao.data_conclusao = datetime.now().isoformat()

        # Adiciona às lições concluídas
        self.curso.licoes_concluidas.append(licao)

        # Atualiza progresso
        prog = self.curso.progresso
        prog.licoes_concluidas = len(self.curso.licoes_concluidas)
        prog.percentual_conclusao = (prog.licoes_concluidas / prog.total_licoes) * 100

        if licao.avaliacao:
            prog.questoes_respondidas += licao.avaliacao.total_questoes
            prog.questoes_corretas += licao.avaliacao.questoes_corretas
            if prog.questoes_respondidas > 0:
                prog.taxa_acerto_geral = (prog.questoes_corretas / prog.questoes_respondidas) * 100

        # Programa revisão
        revisao_data = datetime.now() + timedelta(days=REVIEW_INTERVAL_DAYS)
        prog.revisoes_pendentes.append(f"{licao.id}|{revisao_data.isoformat()}")

        self._save_curso()

    def gerar_feedback(self, avaliacao: Avaliacao) -> str:
        """Gera feedback detalhado sobre a avaliação."""
        respostas_str = ""
        for q in avaliacao.questoes:
            respostas_str += f"\nQuestão {q.numero}: {q.tema}\n"
            respostas_str += f"Resposta: {q.resposta_aluno} ({'✓' if q.resultado == 'correta' else '✗'})\n"
            if q.resultado == "incorreta":
                respostas_str += f"Correta: {q.resposta_correta}\n"

        prompt = get_feedback_prompt(
            total=avaliacao.total_questoes,
            corretas=avaliacao.questoes_corretas,
            respostas=respostas_str
        )

        return self._call_claude(prompt)

    def get_estatisticas(self) -> Dict:
        """Retorna estatísticas completas."""
        prog = self.curso.progresso
        return {
            "licoes_concluidas": prog.licoes_concluidas,
            "total_licoes": prog.total_licoes,
            "percentual": round(prog.percentual_conclusao, 1),
            "questoes_respondidas": prog.questoes_respondidas,
            "questoes_corretas": prog.questoes_corretas,
            "taxa_acerto": round(prog.taxa_acerto_geral, 1),
            "trilhas_total": len(self.curso.trilhas),
            "revisoes_pendentes": len(prog.revisoes_pendentes)
        }

    def importar_licao_json(self, licao_data: dict) -> Licao:
        """Importa uma lição de um JSON (das conversas anteriores)."""
        # Extrai dados do JSON no formato do usuário
        avaliacao = None
        if "avaliacao" in licao_data:
            av_data = licao_data["avaliacao"]
            questoes = []
            for q_data in av_data.get("questoes", []):
                q = Question(
                    numero=q_data.get("numero", 0),
                    tema=q_data.get("tema", ""),
                    cenario=q_data.get("cenario", ""),
                    opcoes={},
                    resposta_correta=q_data.get("resposta_correta", ""),
                    explicacao="",
                    resposta_aluno=q_data.get("resposta_aluno"),
                    resultado=q_data.get("resultado"),
                    conceito_chave=q_data.get("conceito_chave", "")
                )
                questoes.append(q)

            avaliacao = Avaliacao(
                total_questoes=av_data.get("total_questoes", 0),
                questoes_corretas=av_data.get("questoes_corretas", 0),
                taxa_acerto=av_data.get("taxa_acerto", 0),
                status=av_data.get("status", ""),
                questoes=questoes,
                data=licao_data.get("data_conclusao", "")
            )

        topicos = []
        for t_data in licao_data.get("topicos_abordados", []):
            topico = Topico(
                nome=t_data.get("topico", ""),
                subtopicos=t_data.get("subtopicos", [])
            )
            topicos.append(topico)

        licao = Licao(
            id=licao_data.get("licao_id", ""),
            trilha_id=licao_data.get("trilha", "").split(" - ")[0].lower().replace(" ", "_") if licao_data.get("trilha") else "",
            modulo_id=licao_data.get("modulo", ""),
            capitulo_ash_sap=licao_data.get("capitulo_ash_sap", 0),
            titulo=licao_data.get("titulo", ""),
            subtitulo=licao_data.get("subtitulo", ""),
            autores=licao_data.get("autores", []),
            dificuldade=licao_data.get("dificuldade", "intermediário"),
            tempo_estimado_minutos=licao_data.get("tempo_estimado_minutos", 45),
            objetivos_aprendizado=licao_data.get("objetivos_aprendizado", []),
            topicos=topicos,
            pontos_chave=licao_data.get("pontos_chave_memorizacao", []),
            avaliacao=avaliacao,
            status=LessonStatus.CONCLUIDA,
            data_conclusao=licao_data.get("data_conclusao", "")
        )

        # Adiciona ao curso
        self.curso.licoes_concluidas.append(licao)

        # Atualiza progresso
        prog = self.curso.progresso
        prog.licoes_concluidas = len(self.curso.licoes_concluidas)
        prog.percentual_conclusao = (prog.licoes_concluidas / prog.total_licoes) * 100 if prog.total_licoes > 0 else 0

        if avaliacao:
            prog.questoes_respondidas += avaliacao.total_questoes
            prog.questoes_corretas += avaliacao.questoes_corretas
            if prog.questoes_respondidas > 0:
                prog.taxa_acerto_geral = (prog.questoes_corretas / prog.questoes_respondidas) * 100

        self._save_curso()
        return licao


# Singleton
_engine: Optional[StudyEngine] = None


def get_study_engine() -> StudyEngine:
    """Retorna instância do engine."""
    global _engine
    if _engine is None:
        _engine = StudyEngine()
    return _engine

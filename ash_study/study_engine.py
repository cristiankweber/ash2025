"""
study_engine.py - Motor de estudo (Modo Offline)

Este motor funciona 100% offline:
- Importa lições de conversas do Claude
- Navega pelo conteúdo importado
- Gerencia progresso e quizzes
- NÃO requer API key
"""
import json
from datetime import datetime, timedelta
from typing import Optional, List, Dict
from pathlib import Path

from config import DATA_DIR, PASSING_SCORE, REVIEW_INTERVAL_DAYS
from models import (
    CursoASHSAP, Trilha, Modulo, Licao, Question, Avaliacao,
    ProgressoAluno, LessonStatus, Topico
)
from prompts import CHAPTER_INFO


class StudyEngine:
    """Motor de estudo offline."""

    def __init__(self):
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
        """Cria estrutura padrão do curso ASH-SAP."""
        self.curso = CursoASHSAP()

        # Define as 9 trilhas do ASH-SAP
        trilhas_config = [
            {
                "id": "trilha_1",
                "nome": "Hemostasia e Trombose",
                "descricao": "Coagulação, anticoagulantes, trombofilia, hemofilia",
                "capitulos": [15, 16, 17, 18, 19, 20, 21, 22],
                "ordem": 1
            },
            {
                "id": "trilha_2",
                "nome": "Anemias",
                "descricao": "Ferropriva, megaloblástica, hemolítica, aplástica",
                "capitulos": [6, 7, 8, 9, 12, 13, 14, 35, 39],
                "ordem": 2
            },
            {
                "id": "trilha_3",
                "nome": "Hemoglobinopatias",
                "descricao": "Anemia falciforme, talassemias",
                "capitulos": [10, 11],
                "ordem": 3
            },
            {
                "id": "trilha_4",
                "nome": "Plaquetas e Distúrbios Plaquetários",
                "descricao": "PTI, PTT, HIT, microangiopatias",
                "capitulos": [23, 24, 25, 26],
                "ordem": 4
            },
            {
                "id": "trilha_5",
                "nome": "Neoplasias Mieloides",
                "descricao": "SMD, NMP, LMC, LMA",
                "capitulos": [34, 36, 37, 38, 40, 41],
                "ordem": 5
            },
            {
                "id": "trilha_6",
                "nome": "Neoplasias Linfoides",
                "descricao": "LLA, LLC, linfomas, mieloma",
                "capitulos": [42, 43, 44, 45, 46, 47, 48, 49],
                "ordem": 6
            },
            {
                "id": "trilha_7",
                "nome": "Transplante e Terapia Celular",
                "descricao": "TCTH autólogo, alogênico, complicações",
                "capitulos": [30, 31, 32, 33],
                "ordem": 7
            },
            {
                "id": "trilha_8",
                "nome": "Medicina Transfusional",
                "descricao": "Hemocomponentes, reações transfusionais",
                "capitulos": [27, 28, 29],
                "ordem": 8
            },
            {
                "id": "trilha_9",
                "nome": "Hematologia Consultiva",
                "descricao": "Perioperatório, ambulatório, gestação, pediatria",
                "capitulos": [1, 2, 3, 4, 5],
                "ordem": 9
            },
        ]

        for t_config in trilhas_config:
            trilha = Trilha(
                id=t_config["id"],
                nome=t_config["nome"],
                descricao=t_config["descricao"],
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

    def get_trilhas(self) -> List[Trilha]:
        """Retorna lista de trilhas ordenadas."""
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

    def get_licao_by_capitulo(self, capitulo: int) -> Optional[Licao]:
        """Retorna lição de um capítulo específico."""
        for licao in self.curso.licoes_concluidas:
            if licao.capitulo_ash_sap == capitulo:
                return licao
        return None

    def get_capitulos_concluidos(self, trilha_id: str) -> List[int]:
        """Retorna capítulos já concluídos de uma trilha."""
        return [l.capitulo_ash_sap for l in self.curso.licoes_concluidas if l.trilha_id == trilha_id]

    def get_licoes_por_trilha(self, trilha_id: str) -> List[Licao]:
        """Retorna lições concluídas de uma trilha."""
        return [l for l in self.curso.licoes_concluidas if l.trilha_id == trilha_id]

    def avaliar_quiz(self, licao: Licao, respostas: Dict[int, str]) -> Avaliacao:
        """Avalia as respostas do quiz de uma lição importada."""
        if not licao.avaliacao or not licao.avaliacao.questoes:
            return None

        questoes = licao.avaliacao.questoes
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

        return avaliacao

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
        """
        Importa uma lição de um JSON (das conversas do Claude).

        Aceita o formato do JSON que você compartilhou.
        """
        # Extrai avaliação se existir
        avaliacao = None
        if "avaliacao" in licao_data:
            av_data = licao_data["avaliacao"]
            questoes = []
            for q_data in av_data.get("questoes", []):
                q = Question(
                    numero=q_data.get("numero", len(questoes) + 1),
                    tema=q_data.get("tema", ""),
                    cenario=q_data.get("cenario", ""),
                    opcoes=q_data.get("opcoes", {}),
                    resposta_correta=q_data.get("resposta_correta", ""),
                    explicacao=q_data.get("explicacao", ""),
                    resposta_aluno=q_data.get("resposta_aluno"),
                    resultado=q_data.get("resultado"),
                    conceito_chave=q_data.get("conceito_chave", "")
                )
                questoes.append(q)

            avaliacao = Avaliacao(
                total_questoes=av_data.get("total_questoes", len(questoes)),
                questoes_corretas=av_data.get("questoes_corretas", 0),
                taxa_acerto=av_data.get("taxa_acerto", 0),
                status=av_data.get("status", "importado"),
                questoes=questoes,
                data=licao_data.get("data_conclusao", datetime.now().isoformat())
            )

        # Extrai tópicos
        topicos = []
        for t_data in licao_data.get("topicos_abordados", []):
            topico = Topico(
                nome=t_data.get("topico", t_data.get("nome", "")),
                subtopicos=t_data.get("subtopicos", [])
            )
            topicos.append(topico)

        # Identifica trilha pelo nome
        trilha_str = licao_data.get("trilha", "")
        trilha_id = self._identificar_trilha(trilha_str, licao_data.get("capitulo_ash_sap", 0))

        # Cria objeto da lição
        licao = Licao(
            id=licao_data.get("licao_id", f"licao_importada_{datetime.now().timestamp()}"),
            trilha_id=trilha_id,
            modulo_id=licao_data.get("modulo", ""),
            capitulo_ash_sap=licao_data.get("capitulo_ash_sap", 0),
            titulo=licao_data.get("titulo", "Lição Importada"),
            subtitulo=licao_data.get("subtitulo", ""),
            autores=licao_data.get("autores", []),
            dificuldade=licao_data.get("dificuldade", "intermediário"),
            tempo_estimado_minutos=licao_data.get("tempo_estimado_minutos", 45),
            objetivos_aprendizado=licao_data.get("objetivos_aprendizado", []),
            topicos=topicos,
            conteudo=licao_data.get("conteudo", ""),
            pontos_chave=licao_data.get("pontos_chave_memorizacao", licao_data.get("pontos_chave", [])),
            avaliacao=avaliacao,
            status=LessonStatus.CONCLUIDA,
            data_inicio=licao_data.get("data_inicio"),
            data_conclusao=licao_data.get("data_conclusao", datetime.now().isoformat())
        )

        # Verifica se já existe lição para este capítulo
        existing = self.get_licao_by_capitulo(licao.capitulo_ash_sap)
        if existing:
            # Atualiza existente
            self.curso.licoes_concluidas.remove(existing)

        # Adiciona ao curso
        self.curso.licoes_concluidas.append(licao)

        # Atualiza progresso
        self._atualizar_progresso()

        self._save_curso()
        return licao

    def _identificar_trilha(self, trilha_str: str, capitulo: int) -> str:
        """Identifica a trilha pelo nome ou capítulo."""
        trilha_str_lower = trilha_str.lower()

        # Mapeamento por palavras-chave
        mapeamento = {
            "trilha_1": ["hemostasia", "trombose", "coagula"],
            "trilha_2": ["anemia", "ferro", "megaloblast"],
            "trilha_3": ["hemoglobinopat", "falciforme", "talassemia"],
            "trilha_4": ["plaqueta", "pti", "ptt", "hit"],
            "trilha_5": ["mieloid", "smd", "nmp", "lmc", "lma"],
            "trilha_6": ["linfoid", "lla", "llc", "linfoma", "mieloma"],
            "trilha_7": ["transplante", "tcth", "terapia celular"],
            "trilha_8": ["transfusion", "hemocomponente"],
            "trilha_9": ["consultiv", "perioper", "ambulat", "gestação"],
        }

        for trilha_id, keywords in mapeamento.items():
            for kw in keywords:
                if kw in trilha_str_lower:
                    return trilha_id

        # Fallback: identifica pelo capítulo
        for trilha in self.curso.trilhas:
            if capitulo in trilha.capitulos:
                return trilha.id

        return "trilha_9"  # Default

    def _atualizar_progresso(self):
        """Atualiza estatísticas de progresso."""
        prog = self.curso.progresso
        prog.licoes_concluidas = len(self.curso.licoes_concluidas)
        prog.percentual_conclusao = (prog.licoes_concluidas / prog.total_licoes) * 100 if prog.total_licoes > 0 else 0

        # Soma questões
        total_q = 0
        corretas_q = 0
        for licao in self.curso.licoes_concluidas:
            if licao.avaliacao:
                total_q += licao.avaliacao.total_questoes
                corretas_q += licao.avaliacao.questoes_corretas

        prog.questoes_respondidas = total_q
        prog.questoes_corretas = corretas_q
        prog.taxa_acerto_geral = (corretas_q / total_q) * 100 if total_q > 0 else 0

        prog.ultimo_acesso = datetime.now().isoformat()

    def importar_json_completo(self, data: dict) -> int:
        """
        Importa um JSON completo (com múltiplas lições).

        Aceita o formato exato do JSON que você compartilhou.
        """
        count = 0

        # Se tem "licoes_concluidas", importa todas
        if "licoes_concluidas" in data:
            for licao_data in data["licoes_concluidas"]:
                self.importar_licao_json(licao_data)
                count += 1

        # Se tem "progresso_aluno", atualiza
        if "progresso_aluno" in data:
            prog_data = data["progresso_aluno"]
            prog = self.curso.progresso
            prog.trilha_atual = prog_data.get("trilha_atual", prog.trilha_atual)
            prog.modulo_atual = prog_data.get("modulo_atual", prog.modulo_atual)
            prog.dias_consecutivos = prog_data.get("dias_consecutivos", prog.dias_consecutivos)

        self._save_curso()
        return count

    def exportar_progresso(self) -> dict:
        """Exporta o progresso atual em formato JSON."""
        return self.curso.to_dict()


# Singleton
_engine: Optional[StudyEngine] = None


def get_study_engine() -> StudyEngine:
    """Retorna instância do engine."""
    global _engine
    if _engine is None:
        _engine = StudyEngine()
    return _engine

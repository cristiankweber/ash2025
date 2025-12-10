"""
models.py - Modelos de dados da plataforma ASH-SAP Study
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime, date
from enum import Enum
import json


class LessonStatus(str, Enum):
    NAO_INICIADA = "não_iniciada"
    EM_PROGRESSO = "em_progresso"
    CONCLUIDA = "concluída"
    REVISAO_PENDENTE = "revisão_pendente"


class Difficulty(str, Enum):
    BASICO = "básico"
    INTERMEDIARIO = "intermediário"
    AVANCADO = "avançado"


@dataclass
class Question:
    """Questão de avaliação."""
    numero: int
    tema: str
    cenario: str
    opcoes: Dict[str, str]
    resposta_correta: str
    explicacao: str
    resposta_aluno: Optional[str] = None
    resultado: Optional[str] = None  # "correta" ou "incorreta"
    conceito_chave: str = ""


@dataclass
class Topico:
    """Tópico dentro de uma lição."""
    nome: str
    subtopicos: List[str] = field(default_factory=list)
    concluido: bool = False


@dataclass
class Avaliacao:
    """Resultado da avaliação de uma lição."""
    total_questoes: int
    questoes_corretas: int
    taxa_acerto: float
    status: str  # "excelente", "bom", "revisao_necessaria"
    questoes: List[Question] = field(default_factory=list)
    data: str = ""

    def to_dict(self) -> dict:
        return {
            "total_questoes": self.total_questoes,
            "questoes_corretas": self.questoes_corretas,
            "taxa_acerto": self.taxa_acerto,
            "status": self.status,
            "questoes": [vars(q) for q in self.questoes],
            "data": self.data
        }


@dataclass
class AnaliseDesempenho:
    """Análise do desempenho do aluno em uma lição."""
    pontos_fortes: List[str] = field(default_factory=list)
    areas_reforco: List[Dict] = field(default_factory=list)
    revisao_programada: str = ""


@dataclass
class Licao:
    """Uma lição completa."""
    id: str
    trilha_id: str
    modulo_id: str
    capitulo_ash_sap: int
    titulo: str
    subtitulo: str = ""
    autores: List[str] = field(default_factory=list)
    dificuldade: str = "intermediário"
    tempo_estimado_minutos: int = 45
    objetivos_aprendizado: List[str] = field(default_factory=list)
    topicos: List[Topico] = field(default_factory=list)
    conteudo: str = ""  # Conteúdo gerado pelo Claude
    pontos_chave: List[str] = field(default_factory=list)
    avaliacao: Optional[Avaliacao] = None
    analise_desempenho: Optional[AnaliseDesempenho] = None
    status: LessonStatus = LessonStatus.NAO_INICIADA
    data_inicio: Optional[str] = None
    data_conclusao: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "trilha_id": self.trilha_id,
            "modulo_id": self.modulo_id,
            "capitulo_ash_sap": self.capitulo_ash_sap,
            "titulo": self.titulo,
            "subtitulo": self.subtitulo,
            "autores": self.autores,
            "dificuldade": self.dificuldade,
            "tempo_estimado_minutos": self.tempo_estimado_minutos,
            "objetivos_aprendizado": self.objetivos_aprendizado,
            "topicos": [{"nome": t.nome, "subtopicos": t.subtopicos, "concluido": t.concluido} for t in self.topicos],
            "conteudo": self.conteudo,
            "pontos_chave": self.pontos_chave,
            "avaliacao": self.avaliacao.to_dict() if self.avaliacao else None,
            "status": self.status.value,
            "data_inicio": self.data_inicio,
            "data_conclusao": self.data_conclusao
        }


@dataclass
class Modulo:
    """Um módulo dentro de uma trilha."""
    id: str
    nome: str
    descricao: str = ""
    licoes: List[str] = field(default_factory=list)  # IDs das lições
    status: LessonStatus = LessonStatus.NAO_INICIADA


@dataclass
class Trilha:
    """Uma trilha de aprendizado."""
    id: str
    nome: str
    descricao: str = ""
    capitulos: List[int] = field(default_factory=list)  # Capítulos do ASH-SAP
    modulos: List[Modulo] = field(default_factory=list)
    status: LessonStatus = LessonStatus.NAO_INICIADA
    ordem: int = 0

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "nome": self.nome,
            "descricao": self.descricao,
            "capitulos": self.capitulos,
            "modulos": [{"id": m.id, "nome": m.nome, "licoes": m.licoes, "status": m.status.value} for m in self.modulos],
            "status": self.status.value,
            "ordem": self.ordem
        }


@dataclass
class ProgressoAluno:
    """Progresso geral do aluno."""
    licoes_concluidas: int = 0
    total_licoes: int = 0
    percentual_conclusao: float = 0.0
    questoes_respondidas: int = 0
    questoes_corretas: int = 0
    taxa_acerto_geral: float = 0.0
    dias_consecutivos: int = 0
    ultimo_acesso: str = ""
    trilha_atual: str = ""
    modulo_atual: str = ""
    licao_atual: str = ""
    revisoes_pendentes: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "licoes_concluidas": self.licoes_concluidas,
            "total_licoes": self.total_licoes,
            "percentual_conclusao": self.percentual_conclusao,
            "questoes_respondidas": self.questoes_respondidas,
            "questoes_corretas": self.questoes_corretas,
            "taxa_acerto_geral": self.taxa_acerto_geral,
            "dias_consecutivos": self.dias_consecutivos,
            "ultimo_acesso": self.ultimo_acesso,
            "trilha_atual": self.trilha_atual,
            "modulo_atual": self.modulo_atual,
            "licao_atual": self.licao_atual,
            "revisoes_pendentes": self.revisoes_pendentes
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ProgressoAluno":
        return cls(**data)


@dataclass
class Alerta:
    """Alerta do sistema."""
    tipo: str
    prioridade: str
    mensagem: str
    data_criacao: str
    dados: Dict = field(default_factory=dict)


@dataclass
class CursoASHSAP:
    """Estrutura completa do curso ASH-SAP."""
    titulo: str = "ASH-SAP 9th Edition 2025"
    total_paginas: int = 643
    total_capitulos: int = 49
    trilhas: List[Trilha] = field(default_factory=list)
    progresso: ProgressoAluno = field(default_factory=ProgressoAluno)
    licoes_concluidas: List[Licao] = field(default_factory=list)
    alertas: List[Alerta] = field(default_factory=list)

    def get_trilha(self, trilha_id: str) -> Optional[Trilha]:
        """Retorna uma trilha pelo ID."""
        for trilha in self.trilhas:
            if trilha.id == trilha_id:
                return trilha
        return None

    def get_proxima_licao(self, trilha_id: str) -> Optional[int]:
        """Retorna o próximo capítulo a estudar em uma trilha."""
        trilha = self.get_trilha(trilha_id)
        if not trilha:
            return None

        # Encontra capítulos já concluídos
        caps_concluidos = {l.capitulo_ash_sap for l in self.licoes_concluidas if l.trilha_id == trilha_id}

        # Retorna o primeiro capítulo não concluído
        for cap in trilha.capitulos:
            if cap not in caps_concluidos:
                return cap
        return None

    def to_dict(self) -> dict:
        return {
            "titulo": self.titulo,
            "total_paginas": self.total_paginas,
            "total_capitulos": self.total_capitulos,
            "trilhas": [t.to_dict() for t in self.trilhas],
            "progresso": self.progresso.to_dict(),
            "licoes_concluidas": [l.to_dict() for l in self.licoes_concluidas]
        }

    def save(self, filepath: str):
        """Salva o estado do curso em JSON."""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)

    @classmethod
    def load(cls, filepath: str) -> "CursoASHSAP":
        """Carrega o curso de um arquivo JSON."""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        curso = cls(
            titulo=data.get("titulo", "ASH-SAP"),
            total_paginas=data.get("total_paginas", 643),
            total_capitulos=data.get("total_capitulos", 49)
        )

        # Carrega trilhas
        for t_data in data.get("trilhas", []):
            modulos = [
                Modulo(
                    id=m["id"],
                    nome=m["nome"],
                    licoes=m.get("licoes", []),
                    status=LessonStatus(m.get("status", "não_iniciada"))
                )
                for m in t_data.get("modulos", [])
            ]
            trilha = Trilha(
                id=t_data["id"],
                nome=t_data["nome"],
                descricao=t_data.get("descricao", ""),
                capitulos=t_data.get("capitulos", []),
                modulos=modulos,
                status=LessonStatus(t_data.get("status", "não_iniciada")),
                ordem=t_data.get("ordem", 0)
            )
            curso.trilhas.append(trilha)

        # Carrega progresso
        if "progresso" in data:
            curso.progresso = ProgressoAluno.from_dict(data["progresso"])

        return curso

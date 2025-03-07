from pydantic import BaseModel

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from src.core.repositorio.baseModel import Base, TimestampMixin, TimestampMixinSchema, UuidMixin, UuidMixinSchema

"""Mixin é classe de abstração do SQLAlchemy que mapeia a entidade no banco"""
class ProcessoMixin(Base, UuidMixin, TimestampMixin):

    __tablename__ = "processo"
    NumeroProcesso: Mapped[str] = mapped_column(String(255),nullable=True, unique=True, index=True)
    NumeroProcessoConsulta: Mapped[str] = mapped_column(String(255),nullable=True, index=True)
    Classe: Mapped[str] = mapped_column(String(255),nullable=True)
    NomePoloPassivo: Mapped[str] = mapped_column(String(255),nullable=True)
    NomePoloAtivo: Mapped[str] = mapped_column(String(255),nullable=True)
    CpfCNPJPoloPassivo: Mapped[str] = mapped_column(String(255),nullable=True)
    CpfCNPJNomePoloAtivo: Mapped[str] = mapped_column(String(255),nullable=True)
    Assunto: Mapped[str] = mapped_column(String(255),nullable=True)
    Valor: Mapped[str] = mapped_column(String(255),nullable=True)
    Serventia: Mapped[str] = mapped_column(String(255),nullable=True)
    Serventia2: Mapped[str] = mapped_column(String(255),nullable=True)
    
"""BaseModel é uma abstração para validação e tornar a estrutura apta a trabalhar com orm"""
class ProcessoSchemma(BaseModel):
        NumeroProcesso : str
        NumeroProcessoConsulta : str
        Classe : str
        NomePoloPassivo : str
        NomePoloAtivo : str
        CpfCNPJPoloPassivo : str
        CpfCNPJNomePoloAtivo : str
        Assunto : str
        Valor : str
        Serventia : str
        
class Processo(ProcessoSchemma, UuidMixinSchema, TimestampMixinSchema):
        NumeroProcesso : str
        NumeroProcessoConsulta : str
        Classe : str
        NomePoloPassivo : str
        NomePoloAtivo : str
        CpfCNPJPoloPassivo : str
        CpfCNPJNomePoloAtivo : str
        Assunto : str
        Valor : str
        Serventia : str

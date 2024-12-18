from pydantic import BaseModel

from sqlalchemy import ForeignKey, String, Integer,Float,Numeric, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.core.repositorio.baseModel import Base, TimestampMixin, TimestampMixinSchema, UuidMixin, UuidMixinSchema

"""Mixin é classe de abstração do SQLAlchemy que mapeia a entidade no banco"""
class ProcessoMixin(Base, UuidMixin, TimestampMixin):

    __tablename__ = "processo"
    NumeroProcesso: Mapped[str] = mapped_column(String(255),nullable=True, unique=True, index=True)
    NumeroProcessoConsulta: Mapped[str] = mapped_column(String(255),nullable=True, unique=False, index=True)
    Classe: Mapped[str] = mapped_column(Text(),nullable=True)
    NomePoloPassivo: Mapped[str] = mapped_column(Text(),nullable=True)
    NomePoloAtivo: Mapped[str] = mapped_column(Text(),nullable=True)
    CpfCNPJPoloPassivo: Mapped[str] = mapped_column(Text(),nullable=True)
    CpfCNPJNomePoloAtivo: Mapped[str] = mapped_column(Text(),nullable=True)
    Assunto: Mapped[str] = mapped_column(Text(),nullable=True)
    
    Valor: Mapped[Float] = mapped_column(Float(),nullable=True)
    
    Serventia: Mapped[str] = mapped_column(Text(),nullable=True)
    Serventia2: Mapped[str] = mapped_column(Text(),nullable=True)

    meta_processo_id: Mapped[str] = mapped_column(ForeignKey('metaProcesso.uuid'))

    meta_processo: Mapped['MetaProcessoMixin'] = relationship("MetaProcessoMixin")
    
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
        meta_processo_id : str
        
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
        meta_processo_id : str
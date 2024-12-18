from datetime import datetime
from pydantic import BaseModel

from sqlalchemy import DateTime, String, text
from sqlalchemy.orm import Mapped, mapped_column
from src.app.dominio.basicos.Enumeradores.enumeradorTipoProcesso import TipoDeProcesso
from src.core.repositorio.baseModel import Base, TimestampMixin, TimestampMixinSchema, UuidMixin, UuidMixinSchema

"""Mixin é classe de abstração do SQLAlchemy que mapeia a entidade no banco"""
class MetaProcessoMixin(Base, UuidMixin, TimestampMixin):

    __tablename__ = "metaProcesso"
    NumeroProcesso: Mapped[str] = mapped_column(String(255),nullable=False, unique=True, index=True)
    NumeroProcessoConsulta: Mapped[str] = mapped_column(String(255),nullable=False, unique=False, index=True)
    Tipo: Mapped[str] = mapped_column(String(255),nullable=False)
    DataPublicacao: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP")
    )
    
"""BaseModel é uma abstração para validação e tornar a estrutura apta a trabalhar com orm"""
class MetaProcessoSchemma(BaseModel):
        NumeroProcesso : str
        NumeroProcessoConsulta : str
        Tipo : str = ""
        DataPublicacao: datetime | None = None

        # Método para adicionar um tipo, se ele não existir
        def add_tipo(self, novo_tipo: TipoDeProcesso):
                if novo_tipo.value not in self.Tipo.split(","):
                        if self.Tipo:
                                self.Tipo += f",{novo_tipo.value}"
                        else:
                                self.Tipo = novo_tipo.value
                        return self.Tipo

        # Método para remover um tipo, se ele existir
        def remove_tipo(self, tipo_a_remover: TipoDeProcesso):
            tipos = self.Tipo.split(",")  # Divide a string em uma lista
            if tipo_a_remover.value in tipos:
              tipos.remove(tipo_a_remover.value)  # Remove o tipo, se existir
              self.Tipo = ",".join(tipos)  # Reconstrói a string
            return self.Tipo
        
class MetaProcesso(MetaProcessoSchemma, UuidMixinSchema, TimestampMixinSchema):
        NumeroProcesso : str
        NumeroProcessoConsulta : str
        Tipo : str
        DataPublicacao: datetime | None = None

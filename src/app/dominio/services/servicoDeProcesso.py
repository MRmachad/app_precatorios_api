from datetime import datetime
from sqlalchemy import desc, select
from src.app.dominio.models.dadosTribunais.metaProcesso import MetaProcessoMixin
from src.app.dominio.models.dadosTribunais.processo import ProcessoMixin
from src.core.repositorio.servicoBase import ServicoBase, SnippetException
from src.core.repositorio.session import Session

class ServicoDeProcesso(ServicoBase):

    def __init__(self,session : Session) -> None:
        super().__init__(ProcessoMixin, session)

    async def obtenha_por_numeroProcesso(
         self,
        numero_processo: str,
        column: str = "NumeroProcesso",
        with_for_update: bool = False,
    ) -> ProcessoMixin:
        try:
            q = select(self.model).where(getattr(self.model, column) == numero_processo)
        except AttributeError:
            raise SnippetException(
                f"Column {column} not found on {self.model.__tablename__}.",
            )

        if with_for_update:
            q = q.with_for_update()

        results = await self.unidadeDeTrabalho.execute(q)
        return results.unique().scalar_one_or_none()
    
    async def obtenha_ultima_data_publicacao(self) -> datetime | None:

        stmt = (
        select(MetaProcessoMixin.DataPublicacao)
        .join(self.model.meta_processo)  
        .order_by(desc(MetaProcessoMixin.DataPublicacao))  
        .limit(1)  
    )

        result = await self.unidadeDeTrabalho.execute(stmt)

        return result.scalars().first()
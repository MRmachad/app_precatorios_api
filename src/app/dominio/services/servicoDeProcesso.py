from sqlalchemy import select
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
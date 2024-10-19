from datetime import datetime
from sqlalchemy import and_, desc, select
from src.app.dominio.models.dadosTribunais.metaProcesso import MetaProcessoMixin
from src.app.dominio.models.dadosTribunais.processo import ProcessoMixin, ProcessoSchemma
from src.core.repositorio.servicoBase import ServicoBase, SnippetException
from src.core.repositorio.session import Session
from src.core.util.gerenciadorDeLog import log_error

class ServicoDeProcesso(ServicoBase):

    def __init__(self,session : Session) -> None:
        super().__init__(ProcessoMixin, session)

    async def adicione_ou_atualize_um_processo(self, processo: ProcessoSchemma):
        try:
            consulta = select(self.model).where(ProcessoMixin.NumeroProcesso == processo.NumeroProcesso)
            resultado = await self.unidadeDeTrabalho.execute(consulta)
            processo_existente : ProcessoMixin = resultado.scalar()

            if processo_existente:
                await self.atualize_por_id(processo, processo_existente.uuid)
            else:
                await self.adicione(processo)

        except Exception as e:
            log_error(e)
            raise SnippetException(f"Erro ao adicionar ou atualizar o processo: {e}") from e

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
    
    async def obtenha_data_primeiro_inexistente(self, execto : list[str] | None = None) -> MetaProcessoMixin | None:
        stmt = select(MetaProcessoMixin).outerjoin(ProcessoMixin, MetaProcessoMixin.uuid == ProcessoMixin.meta_processo_id)

        if execto:
            stmt = stmt.where(and_(ProcessoMixin.meta_processo_id == None, MetaProcessoMixin.NumeroProcesso.not_in(execto)))
        else:
            stmt = stmt.where(ProcessoMixin.meta_processo_id == None) 
            
        result = await self.unidadeDeTrabalho.execute(stmt.order_by(MetaProcessoMixin.created_at).limit(1))

        return result.scalars().first()
from datetime import datetime
from typing import List
from sqlalchemy import desc, select
from src.app.dominio.basicos.Enumeradores.enumeradorTipoProcesso import TipoDeProcesso
from src.app.dominio.models.dadosTribunais.metaProcesso import MetaProcesso, MetaProcessoMixin, MetaProcessoSchemma
from src.app.dominio.models.dadosTribunais.processo import ProcessoMixin
from src.core.repositorio.servicoBase import ServicoBase, SnippetException
from src.core.repositorio.session import Session
from src.core.util.gerenciadorDeLog import log_error

class ServicoDeMetaProcesso(ServicoBase):

    def __init__(self,session : Session) -> None:
        super().__init__(MetaProcessoMixin, session)

    async def obtenha_por_numeroProcesso(
         self,
        numero_processo: str,
        column: str = "NumeroProcesso",
        type: TipoDeProcesso = None,
        with_for_update: bool = False,
    ) -> MetaProcessoMixin:
        try:
            if(type == None):
                q = select(self.model).where(getattr(self.model, column) == numero_processo)
            else:                
                q = select(self.model).where(getattr(self.model, column) == numero_processo and getattr(self.model, "Tipo") == type.value)
        except AttributeError:
            raise SnippetException(
                f"Column {column} not found on {self.model.__tablename__}.",
            )

        if with_for_update:
            q = q.with_for_update()

        results = await self.unidadeDeTrabalho.execute(q)
        return results.unique().scalar_one_or_none()
    
    async def adicioneTodosCasoNaoExista(self, data: List[MetaProcessoSchemma]):
        try:
            numeros_de_processos = [processo.NumeroProcesso for processo in data]

            consulta = select(self.model).where(MetaProcessoMixin.NumeroProcesso.in_(numeros_de_processos))
            resultados = await self.unidadeDeTrabalho.execute(consulta)

            todos_resultados = resultados.all()

            if not todos_resultados:              
                await self.adicione_muitos(data)
            else:
                processos_existentes = {row[0].NumeroProcesso for row in todos_resultados}
                processos_para_inserir = [processo for processo in data if processo.NumeroProcesso not in processos_existentes]
                processos_unicos = {}
                for processo in processos_para_inserir:
                    if processo.NumeroProcesso not in processos_unicos:
                        processos_unicos[processo.NumeroProcesso] = processo

                if processos_para_inserir:
                    await self.adicione_muitos(list(processos_unicos.values()))

        except Exception as e:
            await self.unidadeDeTrabalho.revertaTrasacao()
            log_error(e)
            raise SnippetException(f"Unknown error occurred: {e}") from e
        
    async def obtenha_muitos_pag(self, page: int = 1, page_size: int = 10, from_date : datetime = None ) -> List[MetaProcesso]:
        offset = (page - 1) * page_size

        stmt = select(self.model).order_by(self.model.DataPublicacao)
        if from_date is not None:
            stmt.filter(self.model.DataPublicacao > from_date)
        result = await self.unidadeDeTrabalho.execute(stmt.offset(offset).limit(page_size))

        meta_processos = result.scalars().all()

        return meta_processos
    
    async def obtenha_ultima_data_publicacao(self, tipo) -> datetime | None:

        stmt = select(self.model.DataPublicacao).where(self.model.Tipo == tipo).order_by(desc(self.model.DataPublicacao)).limit(1)

        result = await self.unidadeDeTrabalho.execute(stmt)

        return result.scalars().first()

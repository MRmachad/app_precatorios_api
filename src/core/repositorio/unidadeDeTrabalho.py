
from typing import Any
from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.repositorio.baseModel import SnippetModel, SnippetSchema

class UnidadeDeTrabalho:
    
    def __init__(self,_session: AsyncSession) -> None:
        self.session =_session
        pass
    
    async def salveAlteracoes(self):
        await self.session.commit()
        pass

    async def inicieTrasacao(self):
        await self.session.begin()
        pass

    
    async def revertaTrasacao(self):
        await self.session.rollback()
        pass

    async def atualizeModel(self, model : SnippetModel):
        await self.session.refresh(model)
        pass

    async def execute(self, query : Select[Any]):
        return self.session.execute(query)
        pass


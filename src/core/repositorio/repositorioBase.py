from typing import List
import inject
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.repositorio.baseModel import SnippetSchema

class RepositorioBase:
    
    def __init__(self,_session: AsyncSession) -> None:
        self.session =_session
        pass

    def adicione(self, model: SnippetSchema):
        self.session.add(model)
        pass

    def adicioneTodos(self, models: List):
        self.session.add_all(models)
        pass
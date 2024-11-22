
from typing import Any
from sqlalchemy import Select
from sqlalchemy.orm import Session

from src.core.repositorio.baseModel import SnippetModel, SnippetSchema

class UnidadeDeTrabalho:
    
    def __init__(self,_session: Session) -> None:
        self.session =_session
        pass
    
    async def salveAlteracoes(self):
      self.session.commit()
        
    async def inicieTrasacao(self):
       self.session.begin()
    
    async def revertaTrasacao(self):
       self.session.rollback()
    
    async def finaliseTrasacao(self):
       self.session.close()
        
    async def atualizeModel(self, model : SnippetModel):
      self.session.refresh(model)
        
    async def execute(self, query : Select[Any]):
        return self.session.execute(query)
       
        


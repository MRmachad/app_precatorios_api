from pydantic import BaseModel


class ProcessoDTO(BaseModel):
        Id : str
        NumeroProcesso : str
        Classe : str
        Nome : str
        Assunto : str
        Valor : str
        Serventia : str
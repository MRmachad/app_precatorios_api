from abc import ABC, abstractmethod
from typing import Any


class BaseScrapping(ABC):
    
    @abstractmethod
    async def work(self) -> Any:
        """ retorna uma conexão"""
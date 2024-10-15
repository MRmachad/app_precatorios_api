from abc import ABC, abstractmethod
import asyncio
from typing import Any, Literal
from apscheduler.schedulers.background import BackgroundScheduler


class WorkerJustFire(ABC):    

    def __init__(self) -> None:
        pass

    @abstractmethod
    async def job(self) -> Any:
        "do something"
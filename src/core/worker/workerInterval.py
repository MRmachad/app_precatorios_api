from abc import ABC, abstractmethod
import asyncio
from typing import Any, Literal
from apscheduler.schedulers.background import BackgroundScheduler


class WorkerInterval(ABC):    

    start_fist: bool
    scheduler: BackgroundScheduler
    def __init__(self, hour: Literal[2], startFist: bool=False) -> None:
        self.scheduler = BackgroundScheduler()
        self.scheduler.add_job(self.job, 'interval', seconds=hour) 
        self.start_fist = startFist
        pass

    @abstractmethod
    async def job(self) -> Any:
        "do something"
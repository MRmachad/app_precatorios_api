from abc import ABC, abstractmethod
import asyncio
import threading
from typing import Any, Literal
from apscheduler.schedulers.background import BackgroundScheduler


class WorkerCron(ABC):    
    start_fist: bool
    scheduler: BackgroundScheduler
    def __init__(self, hour: Literal[2], startFist: bool=False) -> None:
        self.scheduler = BackgroundScheduler()
        self.scheduler.add_job(self.job, 'cron', hour=hour) 
        self.start_fist = startFist
        pass

    @abstractmethod
    async def job(self) -> Any:
        "do something"

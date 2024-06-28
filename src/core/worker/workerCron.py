from abc import ABC, abstractmethod
import asyncio
import threading
from typing import Any, Literal
from apscheduler.schedulers.background import BackgroundScheduler


class WorkerCron(ABC):    

    def __init__(self, hour: Literal[2], startFist: bool=False) -> None:
        scheduler = BackgroundScheduler()
        scheduler.add_job(self.job, 'cron', hour=hour) 
        scheduler.start()
        
        if startFist:
           asyncio.create_task(self.schedule_async_method(5))
        pass

    @abstractmethod
    async def job(self) -> Any:
        "do something"

    async def schedule_async_method(self, delay: int):
        await asyncio.sleep(delay)
        await self.job()
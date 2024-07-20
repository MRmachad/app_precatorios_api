from abc import ABC, abstractmethod
import asyncio
import threading
from typing import Any, Literal
from apscheduler.schedulers.background import BackgroundScheduler


class WorkerCron(ABC):    
    start_fist: bool
    scheduler: BackgroundScheduler
    def __init__(self, hour: Literal[2], minute : Literal[2]=00,  seconds: Literal[2]=00, startFist: bool=False) -> None:
        self.scheduler = BackgroundScheduler()
        self.hour=hour
        self.minute=minute
        self.seconds=seconds
        self.start_fist = startFist
        
        self.scheduler.add_job(self.run_async_startup_job, 'cron', hour=self.hour, minute=self.minute, second=self.seconds)

    @abstractmethod
    async def job(self) -> Any:
        "do something"
    

    async def startup_job(self):
        try:
            await self.job()
        except Exception as e:
            print(f"An error occurred: {e}")

    def run_async_startup_job(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.startup_job())
        loop.close()  

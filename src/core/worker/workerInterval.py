from abc import ABC, abstractmethod
import asyncio
import threading
from typing import Any, Literal
from apscheduler.schedulers.background import BackgroundScheduler


class WorkerInterval(ABC):    

    def __init__(self, hour: Literal[2], startFist: bool=False) -> None:
        self.scheduler = BackgroundScheduler()
        self.scheduler.add_job(self.run_async_startup_job, 'interval', seconds=hour) 
        self.start_fist = startFist
        pass

    @abstractmethod
    async def job(self) -> Any:
        "do something"
    
    def startup_job(self):
        try:
            asyncio.run(self.job())
        except Exception as e:
            print(f"An error occurred: {e}")

    def run_async_startup_job(self):        
        threading.Thread(target=self.startup_job).start()
from abc import ABC, abstractmethod
import asyncio
import threading
from typing import Any, Literal
from apscheduler.schedulers.background import BackgroundScheduler


class WorkerJustFire(ABC):    

    def __init__(self) -> None:
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
from abc import ABC, abstractmethod
from typing import Any, Literal
from apscheduler.schedulers.background import BackgroundScheduler


class WorkerInterval(ABC):    

    def __init__(self, hour: Literal[2], startFist: bool=False) -> None:
        scheduler = BackgroundScheduler()
        scheduler.add_job(self.job, 'interval', seconds=hour) 
        scheduler.start()
        
        if startFist:
            self.job()

        pass

    @abstractmethod
    def job(self) -> Any:
        "do something"

import importlib
import inspect
import logging
import pkgutil
import os
from typing import Any, List, Type
from src.core.util.gerenciadorDeModulos import get_subclasses, import_submodules
from src.app.dominio.models.scrapping.baseScrapping import BaseScrapping
from src.core.worker.workerCron import WorkerCron


class ScratchWorker(WorkerCron):
    def __init__(self) -> None:
        super().__init__(12,True)

    async def job(self) -> Any:
        import_submodules( "src.app.dominio.models.scrapping")
        for subclass in get_subclasses(BaseScrapping):
            if inspect.isclass(subclass) and not inspect.isabstract(subclass):
                await subclass.work(self)
        

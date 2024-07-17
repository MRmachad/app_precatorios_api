import asyncio
import inspect
import threading
from src.core.util.gerenciadorDeModulos import get_subclasses, import_submodules
from src.core.worker.workerCron import WorkerCron
from src.core.worker.workerInterval import WorkerInterval


async def register_worker():
    import_submodules("src.app.dominio.workes")
    for subclass in get_subclasses(WorkerCron):
        if inspect.isclass(subclass) and not inspect.isabstract(subclass):
            worker = subclass()
            worker.scheduler.start()
            if (worker.start_fist):
                await asyncio.create_task(worker.job())

    for subclass in get_subclasses(WorkerInterval):
        if inspect.isclass(subclass) and not inspect.isabstract(subclass):
            worker = subclass()
            worker.scheduler.start()
            if (worker.start_fist):              
               await asyncio.create_task(worker.job())
    

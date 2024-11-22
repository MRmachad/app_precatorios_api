import asyncio
import inspect
import threading
from src.core.util.gerenciadorDeModulos import get_subclasses, import_submodules
from src.core.worker.workerCron import WorkerCron
from src.core.worker.workerInterval import WorkerInterval
from src.core.worker.workerJustFire import WorkerJustFire


async def register_worker():

    import_submodules("src.app.dominio.workes")
    for subclass in get_subclasses(WorkerCron):
        if inspect.isclass(subclass) and not inspect.isabstract(subclass):
            worker = subclass()
            worker.scheduler.start()
            if (worker.start_fist):
                threading.Thread(target=worker.run_async_startup_job).start()

    for subclass in get_subclasses(WorkerInterval):
        if inspect.isclass(subclass) and not inspect.isabstract(subclass):
            worker = subclass()
            worker.scheduler.start()
            if (worker.start_fist):                            
                threading.Thread(target=worker.run_async_startup_job).start()
               
    for subclass in get_subclasses(WorkerJustFire):
        if inspect.isclass(subclass) and not inspect.isabstract(subclass):
            worker = subclass()            
            threading.Thread(target=worker.run_async_startup_job).start()
    
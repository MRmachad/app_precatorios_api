import asyncio
import inspect
import threading
from typing import Any, List, Type
from src.core.util.gerenciadorDeModulos import get_subclasses, import_submodules
from src.app.dominio.models.scrapping.baseScrapping import BaseScrapping
from src.core.worker.workerCron import WorkerCron


class ScratchWorker(WorkerCron):
    def __init__(self) -> None:
        super().__init__(21, 55,55,True)

    async def job(self) -> Any:
        import_submodules( "src.app.dominio.models.scrapping")
        for subclass in get_subclasses(BaseScrapping):
            if inspect.isclass(subclass) and not inspect.isabstract(subclass):
                try:
                    instance = subclass() 
                    print(f"Iniciando worker {instance.__class__.__name__}.", flush=True)
                    threading.Thread(target=register_Scratch,args=(instance,),).start()
                except Exception as e:
                    print(f"Erro no worker {instance.__class__.__name__}: {e}", flush=True)
                    pass

def register_Scratch(instance:any):
    asyncio.run(instance.work())
          

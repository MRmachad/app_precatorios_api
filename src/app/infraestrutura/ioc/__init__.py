
import inject
from src.app.infraestrutura.ioc.dbConfigurate import ioc_config_db
from src.app.infraestrutura.ioc.workerConfigurate import register_worker
from src.app.infraestrutura.ioc.serviceConfigurate import ioc_config_service

def ioc_config(binder:inject.Binder):
    ioc_config_db(binder)
    ioc_config_service(binder)
    register_worker()
    pass

def register_inversion_control():
    inject.configure(ioc_config,bind_in_runtime=True)
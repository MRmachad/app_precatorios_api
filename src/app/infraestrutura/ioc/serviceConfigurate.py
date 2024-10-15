import inject

from src.app.dominio.facade.azureStore.servicoDeStorageAzure import ServicoDeStorageAzure
from src.app.dominio.services.servicoDeMetaProcesso import ServicoDeMetaProcesso
from src.app.dominio.services.interfaces.servicoDeStorage import ServicoDeStorage
from src.core.repositorio.session import Session
from src.app.dominio.services.servicoDeProcesso import ServicoDeProcesso

def ioc_config_service(binder:inject.Binder):
    
    session = Session()
    binder.bind(ServicoDeStorage, ServicoDeStorageAzure())
    binder.bind(ServicoDeProcesso, ServicoDeProcesso(session))
    binder.bind(ServicoDeMetaProcesso, ServicoDeMetaProcesso(session))
    pass

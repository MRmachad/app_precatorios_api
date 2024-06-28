import inject
from src.core.repositorio.session import Session
from src.core.repositorio.baseModel import Base

def ioc_config_db(binder:inject.Binder):

    session = Session()

    Base.metadata.create_all(bind=session.obtenha_engine())

    binder.bind(Session, session)
    
    pass
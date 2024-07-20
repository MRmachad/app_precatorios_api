import os
import inject
from src.core.repositorio.session import Session
from src.core.repositorio.baseModel import Base
from alembic.config import Config
from alembic import command

def ioc_config_db(binder:inject.Binder):

    session = Session()
    
    alembic_cfg_path = os.path.join('alembic.ini')

    alembic_cfg = Config(alembic_cfg_path)

    command.upgrade(alembic_cfg, 'head')

    binder.bind(Session, session)
    
    pass
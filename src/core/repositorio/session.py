
from sqlalchemy import MetaData
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from config import config

class Session:

    def obtenha_engine(self):
        print(f"Conexão {config.data["connections"]["database"]}")
        return create_engine(config.data["connections"]["database"], echo=True)

    def obtenha_sessao(self):
        engine = self.obtenha_engine()

        return scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
    
    def obtenha_meta_dado(self):
        return MetaData(bind=self.obtenha_engine())
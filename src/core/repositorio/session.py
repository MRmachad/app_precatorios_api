
from sqlalchemy import MetaData, create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

class Session:

    def obtenha_engine(self):
        
        DATABASE_URL = "mariadb+mariadbconnector://root:qwerty@localhost:3366/precatorios"

        return create_engine(DATABASE_URL, echo=True)

    def obtenha_sessao(self):
        engine = self.obtenha_engine()

        return scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
    
    def obtenha_meta_dado(self):
        return MetaData(bind=self.obtenha_engine())
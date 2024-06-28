from uuid import UUID

import inject
from sqlalchemy import create_engine, delete, select
from sqlalchemy.exc import IntegrityError

from sqlalchemy.orm import sessionmaker, scoped_session
from src.core.repositorio.session import Session
from src.core.repositorio.repositorioBase import RepositorioBase
from src.core.repositorio.unidadeDeTrabalho import UnidadeDeTrabalho
from src.core.repositorio.baseModel import SnippetModel, SnippetSchema

class SnippetException(Exception):
    pass


class IntegrityConflictException(Exception):
    pass


class NotFoundException(Exception):

    pass

class ServicoBaseCore:
    model : SnippetModel
    repositorio : RepositorioBase
    unidadeDeTrabalho : UnidadeDeTrabalho
    
    def __init__(self, _model: SnippetModel, unidadeDetrabalho: UnidadeDeTrabalho, repositorio: RepositorioBase) -> None:
        self.model =_model
        self.repositorio = repositorio
        self.unidadeDeTrabalho = unidadeDetrabalho
        pass

class ServicoBase(ServicoBaseCore):

    def __init__(self, _model: SnippetModel, session : Session) -> None:

        valid_session = session.obtenha_sessao()
        unidadeDeTrabalho = UnidadeDeTrabalho(valid_session)
        repositorioBase = RepositorioBase(valid_session)
        
        super().__init__( _model, unidadeDeTrabalho, repositorioBase)
        pass

    async def adicione(
        self,
        data: SnippetSchema,
    ) -> SnippetModel:
        try:
            db_model = self.model(**data.model_dump())
            self.repositorio.adicione(db_model)
            await self.unidadeDeTrabalho.salveAlteracoes()
            await self.unidadeDeTrabalho.atualizeModel(db_model)
            
            print("1")
            return db_model
        except IntegrityError:
            raise IntegrityConflictException(
                f"{self.model.__tablename__} conflicts with existing data.",
            )
        except Exception as e:
            raise SnippetException(f"Unknown error occurred: {e}") from e

    async def adicione_muitos(
        self,
        data: list[SnippetSchema],
        return_models: bool = False,
    ) -> list[SnippetModel] | bool:
        db_models = [self.model(**d.model_dump()) for d in data]
        try:
            self.repositorio.adicioneTodos(db_models)
            await self.unidadeDeTrabalho.salveAlteracoes()
        except IntegrityError:
            raise IntegrityConflictException(
                f"{self.model.__tablename__} conflict with existing data.",
            )
        except Exception as e:
            raise SnippetException(f"Unknown error occurred: {e}") from e

        if not return_models:
            return True

        for m in db_models:
            await self.unidadeDeTrabalho.atualizeModel(m)

        return db_models

    async def obtenha_um_por_id(
        self,
        id_: str | UUID,
        column: str = "uuid",
        with_for_update: bool = False,
    ) -> SnippetModel:
        try:
            q = select(self.model).where(getattr(self.model, column) == id_)
        except AttributeError:
            raise SnippetException(
                f"Column {column} not found on {self.model.__tablename__}.",
            )

        if with_for_update:
            q = q.with_for_update()

        results = await self.unidadeDeTrabalho.execute(q)
        return results.unique().scalar_one_or_none()

    async def obtenha_muitos(
        self,
        with_for_update: bool = False,
    ) -> list[SnippetModel]:
        q = select(self.model)
        try:
            q = q
        except AttributeError:
            raise SnippetException(
                f"not found on {self.model.__tablename__}.",
            )

        if with_for_update:
            q = q.with_for_update()
        
        print(q)
        rows = await self.unidadeDeTrabalho.execute(q)
        return rows.unique().scalars().all()
    
    async def obtenha_muitos_por_ids(
        self,
        ids: list[str | UUID] = None,
        column: str = "uuid",
        with_for_update: bool = False,
    ) -> list[SnippetModel]:
        q = select(self.model)
        if ids:
            try:
                q = q.where(getattr(self.model, column).in_(ids))
            except AttributeError:
                raise SnippetException(
                    f"Column {column} not found on {self.model.__tablename__}.",
                )

        if with_for_update:
            q = q.with_for_update()

        rows = await self.unidadeDeTrabalho.execute(q)
        return rows.unique().scalars().all()

    async def atualize_por_id(
        self,
        data: SnippetSchema,
        id_: str | UUID,
        column: str = "uuid",
    ) -> SnippetModel:
        db_model = await self.obtenha_um_por_id(
            self.unidadeDeTrabalho, id_, column=column, with_for_update=True
        )
        if not db_model:
            raise NotFoundException(
                f"{self.model.__tablename__} {column}={id_} not found.",
            )

        values = data.model_dump(exclude_unset=True)
        for k, v in values.items():
            setattr(db_model, k, v)

        try:
            await self.unidadeDeTrabalho.salveAlteracoes()
            await self.unidadeDeTrabalho.atualizeModel(db_model)
            return db_model
        except IntegrityError:
            raise IntegrityConflictException(
                f"{self.model.__tablename__} {column}={id_} conflict with existing data.",
            )

    async def atualize_muitos_por_ids(
        self,
        updates: dict[str | UUID, SnippetSchema],
        column: str = "uuid",
        return_models: bool = False,
    ) -> list[SnippetModel] | bool:
        updates = {str(id): update for id, update in updates.items() if update}
        ids = list(updates.keys())
        db_models = await self.obtenha_muitos_por_ids(
            self.unidadeDeTrabalho, ids=ids, column=column, with_for_update=True
        )

        for db_model in db_models:
            values = updates[str(getattr(db_model, column))].model_dump(
                exclude_unset=True
            )
            for k, v in values.items():
                setattr(db_model, k, v)
            self.unidadeDeTrabalho.adicione(db_model)

        try:
            await self.unidadeDeTrabalho.salveAlteracoes()
        except IntegrityError:
            raise IntegrityConflictException(
                f"{self.model.__tablename__} conflict with existing data.",
            )

        if not return_models:
            return True

        for db_model in db_models:
            await self.unidadeDeTrabalho.atualizeModel(db_model)

        return db_models

    async def remova_por_id(
        self,
        id_: str | UUID,
        column: str = "uuid",
    ) -> int:
        try:
            query = delete(self.model).where(getattr(self.model, column) == id_)
        except AttributeError:
            raise SnippetException(
                f"Column {column} not found on {self.model.__tablename__}.",
            )

        rows = await self.unidadeDeTrabalho.execute(query)
        await self.unidadeDeTrabalho.salveAlteracoes()
        return rows.rowcount

    async def remova_muitos_por_ids(
        self,
        ids: list[str | UUID],
        column: str = "uuid",
    ) -> int:
        if not ids:
            raise SnippetException("No ids provided.")

        try:
            query = delete(self.model).where(getattr(self.model, column).in_(ids))
        except AttributeError:
            raise SnippetException(
                f"Column {column} not found on {self.model.__tablename__}.",
            )

        rows = await self.unidadeDeTrabalho.execute(query)
        await self.unidadeDeTrabalho.salveAlteracoes()
        return rows.rowcount

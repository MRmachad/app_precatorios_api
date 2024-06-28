from datetime import datetime
from typing import TypeAlias
from uuid import UUID as UuidType, uuid4

from pydantic import BaseModel
from sqlalchemy import DateTime, String, create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Mapped, mapped_column

Base = declarative_base()

SnippetModel: TypeAlias = Base # type: ignore
SnippetSchema: TypeAlias = BaseModel

class UuidMixin:
    uuid: Mapped[UuidType] = mapped_column(
        "uuid",
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
        nullable=False,
    )

class UuidMixinSchema(BaseModel):
    uuid: UuidType = None

class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=True,
        index=True,
        server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
    )

class TimestampMixinSchema(BaseModel):
    created_at: datetime | None = None
    updated_at: datetime | None = None


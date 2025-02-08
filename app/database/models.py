import datetime
import enum
from typing import Annotated, Optional

from sqlalchemy import (
    TIMESTAMP,
    DateTime,
    CheckConstraint,
    Column,
    Enum,
    ForeignKey,
    Index,
    BigInteger,
    MetaData,
    PrimaryKeyConstraint,
    String,
    Table,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base


class Users(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True
    )
    admin: Mapped[int]
    alive: Mapped[int]
    unlimit: Mapped[int] 
    count_generate: Mapped[int]
    datetime_of_first_generate: Mapped[DateTime] = mapped_column(DateTime, nullable=True)
    
    
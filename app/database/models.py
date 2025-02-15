from sqlalchemy import (
    DateTime,
    BigInteger,
)
from sqlalchemy.orm import Mapped, mapped_column

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
    datetime_of_first_generate: Mapped[DateTime] = mapped_column(
        DateTime, nullable=True)
    model_for_chat: Mapped[str]
    model_for_image: Mapped[str]
    promt_for_chat: Mapped[str] = mapped_column(nullable=True)

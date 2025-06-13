from sqlalchemy import (
    Boolean,
    DateTime,
    Integer,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Profile(Base):
    __tablename__ = "profile"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_type: Mapped[str] = mapped_column(String(32), nullable=True)
    phone_number: Mapped[str] = mapped_column(String, nullable=True)
    first_name: Mapped[str] = mapped_column(String(50), nullable=True)
    last_name: Mapped[str] = mapped_column(String(50), nullable=True)
    middle_name: Mapped[str] = mapped_column(String(50), nullable=True)
    email: Mapped[str] = mapped_column(String(255), nullable=True)
    gender: Mapped[bool] = mapped_column(Boolean, nullable=True)
    created_date: Mapped[DateTime] = mapped_column(DateTime, nullable=True)
    date_of_birth: Mapped[DateTime] = mapped_column(DateTime, nullable=True)
    updated_date: Mapped[DateTime] = mapped_column(DateTime, nullable=True)

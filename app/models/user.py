from enum import Enum

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import String

from .base import Base


class UserRoleEnum(str, Enum):
    admin = "admin"
    user = "user"


class User(Base):
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
    email: Mapped[str] = mapped_column(String(50), nullable=False)
    role: Mapped[UserRoleEnum] = mapped_column(
        default=UserRoleEnum.user, server_default=UserRoleEnum.user, name="user_role_enum"
    )

    def __repr__(self):
        return f"id={self.id}, username={self.username}, email={self.email}"

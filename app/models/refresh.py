from datetime import datetime
from enum import Enum as PyEnum

from models import Base
from security import REFRESH_TOKEN_EXPIRES_MINUTES
from sqlalchemy import TIMESTAMP, Enum, String, func
from sqlalchemy.orm import Mapped, mapped_column


class TokenStatus(PyEnum, str):
    active = "active"
    deprecated = "deprecated"


class RefreshToken(Base):
    id: Mapped[int] = mapped_column(primary_key=True)
    refresh_token: Mapped[str] = mapped_column(String(255), nullable=False)
    expire_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, nullable=False, server_default=func.now() + func.timedelta(days=REFRESH_TOKEN_EXPIRES_MINUTES)
    )
    status: Mapped[TokenStatus] = mapped_column(
        Enum(TokenStatus, name="token_status"), nullable=False, server_default="active"
    )

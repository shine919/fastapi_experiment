from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Text, Integer, ForeignKey, false, TIMESTAMP, func
from sqlalchemy.orm import mapped_column, Mapped, relationship

if TYPE_CHECKING:
    from . import User
from . import Base


class Todo(Base):
    id:Mapped[int] = mapped_column(primary_key=True)
    title:Mapped[str] = mapped_column(Text,nullable=False)
    description:Mapped[str] = mapped_column(Text,nullable=False)
    completed:Mapped[bool] = mapped_column(default=False,nullable=True,server_default=false())
    user_id:Mapped[int] = mapped_column(Integer,ForeignKey('users.id',ondelete='CASCADE'),nullable=False)


    created_at:Mapped[datetime]= mapped_column(TIMESTAMP,server_default=func.now())
    updated_at:Mapped[datetime]= mapped_column(TIMESTAMP,server_default=func.now(),onupdate=func.now())
    completed_at:Mapped[datetime]= mapped_column(TIMESTAMP,server_default=None,nullable=True)


    def __repr__(self):
        return f"id={self.id}, title={self.title}, description={self.description}, completed={self.completed},user_id={self.user_id},created_at={self.created_at},updated_at={self.updated_at},completed_at={self.completed_at}"
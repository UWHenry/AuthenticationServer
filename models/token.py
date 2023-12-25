from datetime import datetime

from database import Base
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

class Token(Base):
    __tablename__ = "tokens"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    access_token: Mapped[str] = mapped_column(unique=True, index=True, nullable=False)
    refresh_token: Mapped[str] = mapped_column(unique=True, index=True, nullable=False)
    status: Mapped[bool] = mapped_column(default=True, nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    create_time: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)
from datetime import datetime

from database import Base
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    refresh_token: Mapped[str] = mapped_column(nullable=False)
    expiration_time: Mapped[datetime] = mapped_column(nullable=False)
    create_time: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)
from datetime import datetime

from database import Base
from sqlalchemy.orm import Mapped, mapped_column

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(unique=True, index=True, nullable=False)
    email: Mapped[str] = mapped_column(default=None)
    password_hash: Mapped[str] = mapped_column(nullable=False)
    create_time: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)
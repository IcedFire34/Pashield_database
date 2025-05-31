from sqlalchemy import Column, Integer, String, TIMESTAMP, Text, ForeignKey
from sqlalchemy.sql import func
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    name = Column(String, nullable=False)
    surname = Column(String, nullable=False)
    create_date = Column(TIMESTAMP(timezone=True), server_default=func.now())
    last_login_date = Column(TIMESTAMP(timezone=True))

class Password(Base):
    __tablename__ = "passwords"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    hesap_yeri = Column(String, nullable=False)
    username = Column(String, nullable=False)
    password = Column(String, nullable=False)
    icon_name = Column(String)
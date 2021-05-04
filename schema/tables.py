from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Date
from sqlalchemy.orm import relationship

from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)

    entries = relationship("Entry", back_populates="user")


class Entry(Base):
    __tablename__ = "entries"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    amount = Column(Integer)
    frequency = Column(String)
    category = Column(String)
    entry_date = Column(Date)
    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("User", back_populates="entries")

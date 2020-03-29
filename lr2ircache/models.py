from sqlalchemy import Column, Integer, String, LargeBinary, DateTime, UniqueConstraint

from .database import Base


class Item(Base):
    __tablename__ = "item"
    __table_args__ = (UniqueConstraint("type", "lr2_id"),)

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String)
    lr2_id = Column(Integer)
    bmsmd5 = Column(String, unique=True, index=True)
    title = Column(String)


class Ranking(Base):
    __tablename__ = "ranking"

    id = Column(Integer, primary_key=True, index=True)
    bmsmd5 = Column(String, unique=True, index=True)
    ranking = Column(LargeBinary)
    last_accessed = Column(DateTime)


class LR2IRLastAccessed(Base):
    __tablename__ = "lr2ir_last_accessed"

    id = Column(Integer, primary_key=True, index=True)
    last_accessed = Column(DateTime)

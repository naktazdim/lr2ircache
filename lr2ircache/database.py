import os

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = os.environ.get("LR2IRCACHE_DB_URL", "sqlite:///./test.db")

connect_args = {"check_same_thread": False} if SQLALCHEMY_DATABASE_URL[:6] == "sqlite" else {}
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .task_models import Base
import os

DB_PATH = os.getenv('TASK_DB_PATH', f"sqlite:///{os.path.abspath(os.path.join(os.path.dirname(__file__), '../../db/taskrun.db'))}")
engine = create_engine(DB_PATH, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)

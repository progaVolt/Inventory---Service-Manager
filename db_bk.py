from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from pathlib import Path
import os

# -------------------------
# & ".venv\Scripts\python.exe" -c "from db_bk import init_db; init_db(); print('INIT_OK')"
# -------------------------


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DATA_DIR / "app.db"

engine = create_engine(
    f"sqlite:///{DB_PATH.as_posix()}", echo=False, future=True)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


def init_db():
    import models_bk as models_bk
    Base.metadata.create_all(bind=engine)

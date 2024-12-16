from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session

DATABASE_URL = "sqlite:///./ecom2.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

session_local = sessionmaker(autoflush=False, autocommit=False, bind=engine)

Base = declarative_base()


def get_db() -> Session:
    db = session_local()
    try:
        yield db
    finally:
        db.close()

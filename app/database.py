from typing import Any
from collections.abc import Generator


from sqlalchemy.orm.session import Session


from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = (
    "postgresql://postgres:password@127.0.0.1:5432/semantic_db"
)

engine = create_engine(url=SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db() -> Generator[Session, Any, None]:
    """
    Provides a transactional scope for a single database request.

    This dependency function creates a new SQLAlchemy session, yields it to the 
    request handler, and ensures the session is closed once the request 
    is completed, even if an exception occurs.

    Yields:
        Generator[Session, Any, None]: A SQLAlchemy Session object.
    """
    
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

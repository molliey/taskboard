from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from typing import Generator
from app.core.config import settings

# Create database engine based on environment
if settings.TESTING:
    # Use test database for testing
    engine = create_engine(
        settings.TEST_DATABASE_URL,
        connect_args={"check_same_thread": False} if "sqlite" in settings.TEST_DATABASE_URL else {},
        pool_pre_ping=False
    )
else:
    # Production/Development database
    engine = create_engine(
        settings.DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=300,
        pool_size=10,
        max_overflow=20
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Generator:
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


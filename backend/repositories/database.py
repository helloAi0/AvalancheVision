"""Database connection and session factory for AvalancheVision.

Provides dual-engine capabilities supporting both modern asynchronous pipelines
and backwards-compatible synchronous sessions.
"""

import logging
import os
from pathlib import Path
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from backend.core.config import settings

logger = logging.getLogger("AvalancheVision.Database")

# Define the shared Base that models bind to
Base = declarative_base()

# 1. Determine base connection strings
_sync_url = settings.DATABASE_URL
_is_sqlite = False

if "sqlite" in _sync_url.lower() or settings.USE_SQLITE or os.environ.get("USE_SQLITE", "false").lower() == "true":
    _sqlite_path = settings.DATA_PROCESSED_DIR / "avalanchevision.db"
    _sqlite_path.parent.mkdir(parents=True, exist_ok=True)
    _sync_url = f"sqlite:///{_sqlite_path}"
    _async_url = f"sqlite+aiosqlite:///{_sqlite_path}"
    _is_sqlite = True
    
    # Sync Engine Config
    engine = create_engine(_sync_url, connect_args={"check_same_thread": False})
    # Async Engine Config
    async_engine = create_async_engine(_async_url, connect_args={"check_same_thread": False})
    logger.info(f"Initialized dual SQLite engines at: {_sqlite_path}")
else:
    # PostGIS configurations
    _async_url = settings.ASYNC_DATABASE_URL
    
    engine = create_engine(_sync_url, pool_size=5, max_overflow=10, pool_pre_ping=True)
    async_engine = create_async_engine(_async_url, pool_pre_ping=True, pool_size=5, max_overflow=10)
    logger.info(f"Configured Production PostGIS connection engines.")

# 2. Configure Session Factories
SessionLocal = sessionmaker(autocommit=False, autoflush=False, expire_on_commit=False, bind=engine)
AsyncSessionLocal = async_sessionmaker(bind=async_engine, class_=AsyncSession, expire_on_commit=False, autoflush=False)

# 3. Synchronous Dependencies (Keeps current FastAPI routes running)
def get_db():
    """Synchronous FastAPI dependency providing a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 4. Asynchronous Dependencies (Unlocks high-performance Phase 2 endpoints)
async def get_async_db():
    """Asynchronous FastAPI dependency providing a database session."""
    async with AsyncSessionLocal() as session:
        yield session

def is_sqlite_mode() -> bool:
    return _is_sqlite

def check_connection() -> bool:
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return True
    except Exception as exc:
        logger.warning("Database connectivity check failed: %s", exc)
        return False

def init_db():
    """Initializes tables and schemas securely on main.py boot initialization."""
    try:
        from backend.repositories.models import (
            HazardPredictionRecord,
            SatelliteObservationRecord,
            ProcessingJobRecord,
            ModelBenchmarkRecord,
            ProvenanceEventRecord,
        )
        Base.metadata.create_all(bind=engine)
        logger.info("Database schema verification and table creation complete.")
    except Exception as e:
        logger.warning(f"Schema init warning: {e}")

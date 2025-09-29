"""
HTMX-FastAPI Service - Database Configuration

Author: Andrew Stevko
Company: Stevko Cyber Services
License: GPL-3.0 (see LICENSE file for details)
"""

import logging
import os

from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import StaticPool

logger = logging.getLogger(__name__)

# Database URL from environment variable - force psycopg3 driver
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://htmx_user:htmx_password@localhost:5432/htmx_db",
)

# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    poolclass=StaticPool,
    pool_pre_ping=True,
    echo=False,  # Set to True for SQL debugging
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()


def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_driver():
    """Check which database driver is being used"""
    try:
        with engine.connect() as conn:
            # Check the actual driver being used
            driver_name = engine.dialect.driver
            logger.info(f"SQLAlchemy driver: {driver_name}")

            # Check database type by trying PostgreSQL version first, fallback to SQLite
            try:
                result = conn.execute(text("SELECT version()"))
                version = result.fetchone()[0]
                logger.info(f"PostgreSQL version: {version}")
            except Exception:
                # If version() fails, try SQLite version
                try:
                    result = conn.execute(text("SELECT sqlite_version()"))
                    version = result.fetchone()[0]
                    logger.info(f"SQLite version: {version}")
                except Exception as sqlite_error:
                    logger.warning(f"Could not determine database version: {sqlite_error}")

            return driver_name
    except Exception as e:
        logger.error(f"Failed to check driver: {e}")
        return None


def init_database():
    """Initialize database tables"""
    try:
        # Check which driver we're using
        driver = check_driver()
        if driver:
            logger.info(f"Using database driver: {driver}")

        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")

        # Create sequence for auto-incrementing IDs if using PostgreSQL
        if "postgresql" in DATABASE_URL:
            with engine.connect() as conn:
                conn.execute(text("CREATE SEQUENCE IF NOT EXISTS id_sequence START 1;"))
                conn.commit()
                logger.info("Database sequence created successfully")
        else:
            # SQLite uses AUTOINCREMENT automatically
            logger.info("Using SQLite autoincrement (no sequence needed)")

    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


def test_connection():
    """Test database connection"""
    try:
        with engine.connect() as conn:
            # Test connection with a simple query (works for both PostgreSQL and SQLite)
            conn.execute(text("SELECT 1"))
            logger.info("Database connection test successful")
            return True
    except Exception as e:
        logger.error(f"Database connection test failed: {e}")
        return False

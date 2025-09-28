"""
Database configuration and connection management for PostgreSQL
"""

import os
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import logging

logger = logging.getLogger(__name__)

# Database URL from environment variable - force psycopg3 driver
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg://htmx_user:htmx_password@localhost:5432/htmx_db")

# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    poolclass=StaticPool,
    pool_pre_ping=True,
    echo=False  # Set to True for SQL debugging
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
    """Check which PostgreSQL driver is being used"""
    try:
        with engine.connect() as conn:
            # Check if we're using PostgreSQL or SQLite (for testing)
            if "postgresql" in DATABASE_URL:
                result = conn.execute(text("SELECT version()"))
                version = result.fetchone()[0]
                logger.info(f"PostgreSQL version: {version}")
                
                # Check the actual driver being used
                driver_name = engine.dialect.driver
                logger.info(f"SQLAlchemy driver: {driver_name}")
                
                return driver_name
            else:
                # SQLite for testing
                driver_name = engine.dialect.driver
                logger.info(f"SQLAlchemy driver: {driver_name}")
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
            if "postgresql" in DATABASE_URL:
                result = conn.execute(text("SELECT 1"))
            else:
                # SQLite test
                result = conn.execute(text("SELECT 1"))
            logger.info("Database connection test successful")
            return True
    except Exception as e:
        logger.error(f"Database connection test failed: {e}")
        return False
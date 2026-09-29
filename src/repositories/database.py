"""
Singleton database engine and session manager using SQLAlchemy.
Provides connection management for PostgreSQL.
"""
from contextlib import contextmanager
from sqlalchemy import Engine, create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from settings import config
from typing import Generator, AsyncGenerator, Any
from sqlalchemy.engine import Engine, Inspector
from utils.exceptions.custom_app_exception import CustomAppException
from utils.exceptions.error_codes import ErrorCode
from utils.exceptions.http_status import HttpStatusCode


class Database:
    """
    Singleton class that manages the SQLAlchemy engine and session factory.
    Ensures only one database connection pool is created per application lifecycle.
    """

    _instance = None

    def __new__(cls):
        """Returns the existing instance or creates a new singleton instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self)-> None:
        """Initializes the database engine and session factory if not already done."""
        if self._initialized:
            return
        self.engine = self._create_engine()
        self.SessionLocal = sessionmaker(
            bind=self.engine,
            autoflush=False,
            autocommit=False
        )
        self._initialized = True

    def _create_engine(self)-> Engine:
        """
        Builds the PostgreSQL connection URL from config and creates the SQLAlchemy engine.
        """
        db_url = (
            f"postgresql+psycopg2://{config.db_username}:"
            f"{config.db_password}@"
            f"{config.db_host}:"
            f"{config.db_port}/"
            f"{config.db_name}"
        )
        return create_engine(db_url)

    @contextmanager
    def get_db(self)-> Generator[Session,None, None]:
        """
        Context manager that provides a database session with auto-commit and rollback.
        Ensures the session is always closed after use.
        """
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    async def test_connection(self)-> bool:
        """
        Tests the database connection by executing a simple query.
        Raises CustomAppException if the connection fails.
        """
        try:
            with self.engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            return True
        except Exception:
            raise CustomAppException(
                message="Database connection failed",
                code=ErrorCode.DB_CONNECTION_FAIL,
                status_code=HttpStatusCode.SERVICE_UNAVAILABLE
            )

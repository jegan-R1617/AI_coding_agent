"""
Database migration runner for the Multi-Agent Code Pipeline.
Creates required tables on application startup.
"""
from repositories.database import Database
from repositories.schema.schema import Base
from utils.logger import logger

class Migration:
    """Handles database schema creation and teardown."""

    def __init__(self):
        """Initializes the migration with the shared database instance."""
        self.db = Database()

    def create_tables(self) -> None:
        """Creates all SQLAlchemy-defined tables if they do not already exist."""
        try:
            Base.metadata.create_all(bind=self.db.engine)
            logger.info("✓ Database tables created successfully")
        except Exception as e:
            logger.info(f"✗ Error creating tables: {str(e)}")
            raise

    def run_startup_migration(self) -> None:
        """Runs table creation as part of the FastAPI application startup lifecycle."""
        self.create_tables()

migration=Migration()
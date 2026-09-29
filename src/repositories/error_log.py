"""
Repository for persisting application error logs to the database.
"""
from repositories.database import Database
from repositories.schema.schema import ErrorLog as ErrorLogTable
from utils.logger import logger

class ErrorLogRepository:
    """Handles saving error records to the error_logs database table."""

    def __init__(self):
        """Initializes the repository with the shared database instance."""
        self.db = Database()

    def save_error(
        self,
        error_code: str,
        error_message: str,
        file_name: str,
        function_name: str
    ) -> None:
        """
        Persists an error log entry to the database.
        Silently catches any DB write failures to avoid masking the original error.
        """
        try:
            with self.db.get_db() as session:
                log = ErrorLogTable(
                    error_code=error_code,
                    error_message=error_message,
                    file_name=file_name,
                    function_name=function_name
                )
                session.add(log)
        except Exception as db_err:
            logger.info(f"[ErrorLogRepository] Failed to save error log: {db_err}")

error_logger=ErrorLogRepository()

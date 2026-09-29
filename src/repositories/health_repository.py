from utils.exceptions.custom_app_exception import CustomAppException
from utils.exceptions.error_codes import ErrorCode
from utils.exceptions.http_status import HttpStatusCode
from repositories.database import Database
from sqlalchemy import text



class HealthCheckRepository():
    def __init__(self):
        self.db_instance = Database()

    async def health_check_repository(self) :
        """Makes a session with the database to check the health of the database which returns either Healthy or Unhealthy"""
        try:
            flag=await self.db_instance.test_connection()
            if flag:
                return "Connection established"
            return "Cannot establish conection"
        except CustomAppException:
            raise
        except Exception as e:
            raise CustomAppException(
                message=f"Repository error: {str(e)}",
                code=ErrorCode.DATABASE_ERROR,
                status_code=HttpStatusCode.INTERNAL_SERVER_ERROR,
            )
        
health_repository=HealthCheckRepository()
        
          
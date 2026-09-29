from repositories.health_repository import health_repository
from utils.exceptions.custom_app_exception import CustomAppException
from utils.exceptions.error_codes import ErrorCode
from utils.exceptions.http_status import HttpStatusCode
from repositories.error_log import error_logger
class HealthCheckService:

    async def health_check_service(self)-> str:
        """Service function to to check the health of the database which returns a string"""
        
        try:
            health= await health_repository.health_check_repository()
            return health

        except CustomAppException:
            raise
        except Exception as e:
            error_logger.save_error(
            error_code=ErrorCode.INTERNAL_SERVER_ERROR,
            error_message=str(e),
            file_name="health_service.py",
            function_name="health_check_service"
        )
            raise CustomAppException(
                message=f"Unexpected service error during db health check: {str(e)}",
                code=ErrorCode.INTERNAL_SERVER_ERROR,
                status_code=HttpStatusCode.INTERNAL_SERVER_ERROR,
            ) 
        
health_service=HealthCheckService()
"""
Service layer for the Multi-Agent Code Pipeline.
Delegates user requests to the pipeline orchestrator.
"""
from agents.orchestrator import orchestrator
from utils.exceptions.custom_app_exception import CustomAppException
from utils.exceptions.error_codes import ErrorCode
from utils.exceptions.http_status import HttpStatusCode
from repositories.error_log import error_logger
from utils.logger import logger


class PipelineService:
    """Handles business logic for processing user queries through the agent pipeline."""
        

    async def run_pipeline(self, user_query: str) -> str:
        """
        Passes the user query to the orchestrator and returns the pipeline's final output.
        Raises CustomAppException on service-level failures.
        """
        logger.info("Pipeline service started")
        try:
            orches= await orchestrator.run(user_query=user_query)
            logger.info("Pipeline service has been completed...")
            return orches

        except CustomAppException:
            raise
        except Exception as e:
            error_logger.save_error(
                error_code=ErrorCode.SERVICE_ERROR,
                error_message=str(e),
                file_name="service.py",
                function_name="run_pipeline"
            )
            raise CustomAppException(
                message=f"Service error: {str(e)}",
                code=ErrorCode.SERVICE_ERROR,
                status_code=HttpStatusCode.INTERNAL_SERVER_ERROR
            )
        
service=PipelineService()

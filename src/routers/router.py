"""
API router for the Multi-Agent Code Pipeline.
Exposes the pipeline endpoint for processing user queries.
"""
from fastapi import APIRouter, Body
from fastapi.responses import JSONResponse
from models.api_response_dto import APIResponse
from models.code_request import CodeRequest
from services.service import service
from utils.exceptions.custom_app_exception import CustomAppException
from utils.exceptions.error_codes import ErrorCode
from utils.exceptions.http_status import HttpStatusCode
from repositories.error_log import error_logger
from services.health_service import health_service
from utils.logger import logger

router = APIRouter(prefix="/api/v1")


@router.post("/run")
async def run_pipeline_router(
    request: CodeRequest = Body(...)
)->JSONResponse:
    """
    Accepts a natural language user query and routes it through
    the multi-agent pipeline (code, review, or research) based on LLM intent classification.
    Returns the final pipeline output wrapped in a standardized API response then to JSONResponse.
    """
    logger.info("Pipeline router started")
    try:
        
        result = await service.run_pipeline(request.user_query)
        logger.info("Pipeline router has been completed...")
        data = APIResponse(
            data={"result": result},
            code=HttpStatusCode.OK,
            message="Pipeline executed successfully"
        )
        return JSONResponse(
            content=data.to_dict(),
            status_code=data.code
        )

    except CustomAppException:
        raise
    except Exception as e:
        error_logger.save_error(
            error_code=ErrorCode.ROUTER_ERROR,
            error_message=str(e),
            file_name="router.py",
            function_name="run_pipeline_router"
        )
        raise CustomAppException(
            message=f"Router error: {str(e)}",
            code=ErrorCode.ROUTER_ERROR,
            status_code=HttpStatusCode.INTERNAL_SERVER_ERROR
        )

@router.get("/health")
async def health_check_router() -> JSONResponse:
    """Router function to check the health of the database. It returns JSONResponse"""
    try:
        result = await health_service.health_check_service()
        logger.info(result,"result")
        data =APIResponse(
            data=result,
            code=HttpStatusCode.OK
        )
        return JSONResponse(
            content= data.to_dict(),
            status_code=data.code
        )
    except CustomAppException:
        raise
    except Exception as e:
        error_logger.save_error(
            error_code=ErrorCode.INTERNAL_SERVER_ERROR,
            error_message=str(e),
            file_name="router.py",
            function_name="health_check_router"
        )
        raise CustomAppException(
            message=f"Router error: {str(e)}",
            code=ErrorCode.INTERNAL_SERVER_ERROR,
            status_code=HttpStatusCode.INTERNAL_SERVER_ERROR
        )

    


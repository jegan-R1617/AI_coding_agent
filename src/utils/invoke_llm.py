"""
LLM client initialization using AWS Bedrock via LangChain.
Provides a reusable method to get a configured ChatBedrock instance.
"""
import boto3
from langchain_aws import ChatBedrock
from settings import config
from utils.exceptions.custom_app_exception import CustomAppException
from utils.exceptions.error_codes import ErrorCode
from utils.exceptions.http_status import HttpStatusCode


class InvokeLLM:
    """Handles creation of the AWS Bedrock LLM client."""

    async def get_bedrock_client(self):
        """
        Creates and returns a boto3 Bedrock runtime client
        using credentials from application config.
        """
        return boto3.client(
            service_name="bedrock-runtime",
            region_name=config.region,
            aws_access_key_id=config.aws_access_key_id,
            aws_secret_access_key=config.aws_secret_access_key
        )

    async def get_llm(self, max_tokens: int = 2048, temperature: float = 0.7) -> ChatBedrock:
        """
        Initializes and returns a ChatBedrock LLM instance.
        Raises CustomAppException if initialization fails.
        """
        try:
            client = await self.get_bedrock_client()
            return ChatBedrock(
                client=client,
                model_id=config.model_id,
                provider=config.provider,
                model_kwargs={
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                }
            )
        except Exception as e:
            raise CustomAppException(
                message=f"LLM initialization failed: {str(e)}",
                code=ErrorCode.LLM_INITIALIZATION_ERROR,
                status_code=HttpStatusCode.SERVICE_UNAVAILABLE
            )
        
invoke_llm=InvokeLLM()

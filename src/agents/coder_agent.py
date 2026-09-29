"""
Coder Agent responsible for generating code based on user requirements.
Uses the LLM to produce clean, production-ready code solutions.
"""
from langchain_core.messages import SystemMessage, HumanMessage
from agents.system_prompt import coder_agent_prompt
from langchain.agents import create_agent
from utils.invoke_llm import invoke_llm
from utils.exceptions.custom_app_exception import CustomAppException
from utils.exceptions.error_codes import ErrorCode
from utils.exceptions.http_status import HttpStatusCode
from repositories.error_log import error_logger


class CoderAgent:
    """Generates code solutions from user requirements using the LLM."""

    async def generate_code(self, user_query: str, context: str = "") -> str:
        """
        Generates code based on the user query and optional enriched context.
        If context is provided (from the researcher), it is included in the prompt.
        Raises CustomAppException on LLM invocation failure.
        """
        try:
            llm = await invoke_llm.get_llm(max_tokens=2048, temperature=0.5)
            
            user_content = f"Requirement: {user_query}"
            if context:
                user_content += f"\n\nAdditional Research Context:\n{context}"

            messages = [
                SystemMessage(content=coder_agent_prompt),
                HumanMessage(content=user_content)
            ]

            response = await llm.ainvoke(messages)
            return response.content
            #-----------with agent
            # agent=create_agent(
            #     model=llm,
            #     system_prompt=coder_agent_prompt
            # )
            # response=await agent.ainvoke({
            #     "messages":[{"role":"user","content":user_content}]
            # })
            # return response["messages"][-1].content

        except CustomAppException:
            raise
        except Exception as e:
            error_logger.save_error(
                error_code=ErrorCode.CODER_AGENT_ERROR,
                error_message=str(e),
                file_name="coder_agent.py",
                function_name="generate_code"
            )
            raise CustomAppException(
                message=f"Coder agent failed: {str(e)}",
                code=ErrorCode.CODER_AGENT_ERROR,
                status_code=HttpStatusCode.INTERNAL_SERVER_ERROR
            )
        
coder_agent=CoderAgent()

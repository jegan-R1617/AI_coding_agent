"""
Researcher Agent responsible for resolving knowledge gaps and enriching context.
Activated when the review agent fails or when the user requests research directly.
"""
from langchain_core.messages import SystemMessage, HumanMessage
from agents.system_prompt import researcher_agent_prompt
from langchain.agents import create_agent
from utils.invoke_llm import invoke_llm
from utils.exceptions.custom_app_exception import CustomAppException
from utils.exceptions.error_codes import ErrorCode
from utils.exceptions.http_status import HttpStatusCode
from repositories.error_log import error_logger


class ResearcherAgent:
    """Fetches enriched context and best practices to assist code generation or answer research queries."""

    async def research(self, user_query: str, review_feedback: str = "") -> str:
        """
        Performs research on the topic derived from the user query.
        If review feedback is provided, it is used to focus the research
        on the specific issues identified by the review agent.
        Raises CustomAppException on LLM invocation failure.
        """
        try:
            llm = await invoke_llm.get_llm(max_tokens=1024, temperature=0.5)

            user_content = f"Topic / Query: {user_query}"
            if review_feedback:
                user_content += (
                    f"\n\nThe code reviewer identified the following issues:\n{review_feedback}"
                    f"\n\nPlease focus your research on resolving these issues."
                )

            messages = [
                SystemMessage(content=researcher_agent_prompt),
                HumanMessage(content=user_content)
            ]

            response = await llm.ainvoke(messages)
            return response.content
            #------------------with agent
            # agent=create_agent(
            #     model=llm,
            #     system_prompt=researcher_agent_prompt
            # )
            # response=await agent.ainvoke([{
            #     "messages":[{"role":"user", "content":user_content}]
            # }])
            # return response["messages"][-1].content

        except CustomAppException:
            raise
        except Exception as e:
            error_logger.save_error(
                error_code=ErrorCode.RESEARCHER_AGENT_ERROR,
                error_message=str(e),
                file_name="researcher_agent.py",
                function_name="research"
            )
            raise CustomAppException(
                message=f"Researcher agent failed: {str(e)}",
                code=ErrorCode.RESEARCHER_AGENT_ERROR,
                status_code=HttpStatusCode.INTERNAL_SERVER_ERROR
            )
        
researcher_agent=ResearcherAgent()

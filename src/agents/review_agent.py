"""
Review Agent responsible for validating and critiquing generated or user-provided code.
Returns a structured review with a PASS or FAIL status.
"""
from langchain_core.messages import SystemMessage, HumanMessage
from agents.system_prompt import review_agent_prompt
from utils.invoke_llm import invoke_llm
from utils.exceptions.custom_app_exception import CustomAppException
from utils.exceptions.error_codes import ErrorCode
from utils.exceptions.http_status import HttpStatusCode
from repositories.error_log import error_logger
from langchain.agents import create_agent


class ReviewAgent:
    """Reviews code quality and correctness, returning a structured pass/fail assessment."""


    async def review_code(self, user_query: str, code: str) -> dict:
        """
        Reviews the provided code against the original user requirement.
        Returns a dict with keys: 'status' (PASS/FAIL), 'feedback' (full review text).
        Raises CustomAppException on LLM invocation failure.
        """
        try:
            llm = await invoke_llm.get_llm(max_tokens=1024, temperature=0.3)

            user_content = (
                f"Original Requirement: {user_query}\n\n"
                f"Code to Review:\n{code}"
            )

            messages = [
                SystemMessage(content=review_agent_prompt),
                HumanMessage(content=user_content)
            ]

            response = await llm.ainvoke(messages)
            review_text = response.content
            #----------------------with agent
            # agent=create_agent(
            #     model=llm,
            #     system_prompt=review_agent_prompt
            # )
            # response=await agent.ainvoke([{
            #     "messages":[{"role":"user","content":user_content}]
            # }])

            # review_text=response["messages"][-1].content

            status = "PASS" if "STATUS: PASS" in review_text.upper() else "FAIL"

            return {
                "status": status,
                "feedback": review_text
            }

        except CustomAppException:
            raise
        except Exception as e:
            error_logger.save_error(
                error_code=ErrorCode.REVIEW_AGENT_ERROR,
                error_message=str(e),
                file_name="review_agent.py",
                function_name="review_code"
            )
            raise CustomAppException(
                message=f"Review agent failed: {str(e)}",
                code=ErrorCode.REVIEW_AGENT_ERROR,
                status_code=HttpStatusCode.INTERNAL_SERVER_ERROR
            )
        
review_agent=ReviewAgent()

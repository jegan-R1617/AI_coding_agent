"""
Orchestrator for the Multi-Agent Code Pipeline.
Uses LangGraph to manage agent execution flow, shared state,
and conditional routing based on LLM-determined intent.
"""
from typing import TypedDict, Literal
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.graph import StateGraph, END
from utils.logger import logger
from agents.coder_agent import coder_agent
from agents.review_agent import review_agent
from agents.researcher_agent import researcher_agent
from agents.system_prompt import intent_classifier_prompt
from utils.invoke_llm import invoke_llm
from utils.exceptions.custom_app_exception import CustomAppException
from utils.exceptions.error_codes import ErrorCode
from utils.exceptions.http_status import HttpStatusCode
from repositories.error_log import error_logger


# ── Shared Pipeline State ──────────────────────────────────────────────────────

class PipelineState(TypedDict):
    """Shared state passed between all nodes in the LangGraph pipeline."""
    user_query: str               
    intent: str                  
    generated_code: str           
    review_status: str            
    review_feedback: str          
    research_context: str        
    final_output: str             
    retry_count: int              



class PipelineOrchestrator:
    """
    Builds and runs the LangGraph multi-agent pipeline.
    Determines intent, routes to the appropriate agent flow,
    and manages retry logic when code review fails.
    """
    MAX_RETRIES=1


    def __init__(self):
        """Compiles the graph."""
        logger.info("Building graph...")
        self.graph = self._build_graph()


    async def classify_intent_node(self, state: PipelineState) -> PipelineState:
        """
        Calls the LLM with the intent classifier prompt to determine
        whether the user wants to 'code', 'review', or 'research'.
        Sets the 'intent' field in the shared pipeline state.
        """
        try:
            logger.info("Finding the intent of the user query...")

            llm = await invoke_llm.get_llm(max_tokens=10, temperature=0.0)
            messages = [
                SystemMessage(content=intent_classifier_prompt),
                HumanMessage(content=state["user_query"])
            ]
            response = await llm.ainvoke(messages)
            intent = response.content.strip().lower()
            if intent not in ("code", "review", "research"):
                intent = "code"
            logger.info("Intent found...")


            return {"intent": intent}

        except CustomAppException:
            raise
        except Exception as e:
            error_logger.save_error(
                error_code=ErrorCode.INTENT_CLASSIFICATION_ERROR,
                error_message=str(e),
                file_name="orchestrator.py",
                function_name="classify_intent_node"
            )
            raise CustomAppException(
                message=f"Intent classification failed: {str(e)}",
                code=ErrorCode.INTENT_CLASSIFICATION_ERROR,
                status_code=HttpStatusCode.INTERNAL_SERVER_ERROR
            )


    async def coder_node(self, state: PipelineState) -> PipelineState:
        """
        Invokes the CoderAgent to generate code from the user query.
        Passes any existing research context to improve code quality on retries.
        """
        logger.info("Generating code...")

        generated_code = await coder_agent.generate_code(
            user_query=state["user_query"],
            context=state.get("research_context", "")
        )
        logger.info("Code has been generated...")


        return {"generated_code": generated_code}


    async def review_node(self, state: PipelineState) -> PipelineState:
        """
        Invokes the ReviewAgent to validate the generated or user-provided code.
        Stores the review status (PASS/FAIL) and feedback in the pipeline state.
        """
        logger.info("Reviewing the code...")
        result = await review_agent.review_code(
            user_query=state["user_query"],
            code=state["generated_code"]
        )
        logger.info("Code has been reviewed...")


        return {
            "review_status": result["status"],
            "review_feedback": result["feedback"]
        }


    async def researcher_node(self, state: PipelineState) -> PipelineState:
        """
        Invokes the ResearcherAgent to gather enriched context.
        When triggered after a review failure, passes the feedback
        so the research is focused on the identified issues.
        """
        logger.info("Researching for better code")

        context = await researcher_agent.research(
            user_query=state["user_query"],
            review_feedback=state.get("review_feedback", "")
        )
        logger.info("Research has been finished")


        return {
            "research_context": context,
            "retry_count": state.get("retry_count", 0) + 1
        }



    async def final_output_node(self, state: PipelineState) -> PipelineState:
        """
        Assembles the final output for the user based on intent and pipeline results.
        For 'code' intent: returns generated code + review feedback.
        For 'review' intent: returns the review feedback only.
        For 'research' intent: returns the research context only.
        """
        logger.info("Final output...")
        intent = state.get("intent", "code")

        if intent == "research":
            output = state.get("research_context", "No research output available.")

        elif intent == "review":
            output = state.get("review_feedback", "No review output available.")

        else:
            # code flow
            output = (
                f"### Generated Code\n\n{state.get('generated_code', '')}\n\n"
                f"### Review\n\n{state.get('review_feedback', '')}"
            )

        # logger.info(f"\n[FINAL OUTPUT] Intent: {intent.upper()}")
        logger.info(f"[FINAL OUTPUT] Result:\n{output}")
        # print(state.get('retry_count'))

        return {"final_output": output}



    def route_by_intent(self, state: PipelineState) -> Literal["coder_node", "review_node", "researcher_node"]:
        """
        Reads the classified intent from state and routes to the correct starting node.
        - 'code'     → coder_node (full pipeline)
        - 'review'   → review_node (review only)
        - 'research' → researcher_node (research only)
        """
        logger.info("Routing based on intent...")
        intent = state.get("intent", "code")
        if intent == "code":
            return "coder_node"
        elif intent == "review":
            return "review_node"
        else:
            return "researcher_node"

   

    def route_after_review(self, state: PipelineState) -> Literal["researcher_node", "final_output_node"]:
        """
        Reads the review status from state and decides the next step.
        - PASS or max retries reached → final_output_node
        - FAIL and retries remaining  → researcher_node (to enrich context and retry)
        """
        logger.info("Routing after review...")
        if state.get("review_status") == "PASS":
            return "final_output_node"
        if state.get("retry_count", 0) >= self.MAX_RETRIES:
            return "final_output_node"
        return "researcher_node"


    def route_after_research(self, state: PipelineState) -> Literal["coder_node", "final_output_node"]:
        """
        After research, decides whether to loop back to the coder (code flow)
        or go directly to the final output (research-only flow).
        """
        logger.info("Routing after research...")
        intent = state.get("intent", "code")
        if intent == "code":
            return "coder_node"
        return "final_output_node"


    def _build_graph(self):
        """
        Constructs and compiles the LangGraph StateGraph with all nodes,
        edges, and conditional routing logic.
        """
        graph = StateGraph(PipelineState)

        # Register nodes
        graph.add_node("classify_intent_node", self.classify_intent_node)
        graph.add_node("coder_node", self.coder_node)
        graph.add_node("review_node", self.review_node)
        graph.add_node("researcher_node", self.researcher_node)
        graph.add_node("final_output_node", self.final_output_node)

        # Entry point
        graph.set_entry_point("classify_intent_node")

        # Route after intent classification
        graph.add_conditional_edges(
            "classify_intent_node",
            self.route_by_intent,
            {
                "coder_node": "coder_node",
                "review_node": "review_node",
                "researcher_node": "researcher_node"
            }
        )

        # Code flow: coder → review
        graph.add_edge("coder_node", "review_node")

        # Review flow: conditional — pass → final, fail → researcher
        graph.add_conditional_edges(
            "review_node",
            self.route_after_review,
            {
                "researcher_node": "researcher_node",
                "final_output_node": "final_output_node"
            }
        )

        # After research: loop back to coder (code flow) or go to final (research-only)
        graph.add_conditional_edges(
            "researcher_node",
            self.route_after_research,
            {
                "coder_node": "coder_node",
                "final_output_node": "final_output_node"
            }
        )

        # Final output → END
        graph.add_edge("final_output_node", END)
        logger.info("Graph built...")
        return graph.compile()


    async def run(self, user_query: str) -> str:
        """
        Runs the full LangGraph pipeline with the given user query.
        Initializes shared state and returns the final output string.
        Raises CustomAppException on pipeline-level failures.
        """
        try:
            logger.info("Pipeline orchestration has been started...")
            initial_state: PipelineState = {
                "user_query": user_query,
                "intent": "",
                "generated_code": "",
                "review_status": "",
                "review_feedback": "",
                "research_context": "",
                "final_output": "",
                "retry_count": 0
            }

            result = await self.graph.ainvoke(initial_state)
            logger.info("Pipeline orchestration completed...")
            return result.get("final_output", "No output generated.")

        except CustomAppException:
            raise
        except Exception as e:
            error_logger.save_error(
                error_code=ErrorCode.ORCHESTRATOR_ERROR,
                error_message=str(e),
                file_name="orchestrator.py",
                function_name="run"
            )
            raise CustomAppException(
                message=f"Pipeline execution failed: {str(e)}",
                code=ErrorCode.ORCHESTRATOR_ERROR,
                status_code=HttpStatusCode.INTERNAL_SERVER_ERROR
            )
        
orchestrator=PipelineOrchestrator()
"""
Application-specific error codes for the Multi-Agent Code Pipeline.
Only includes codes that are actually used in this application.
"""


class ErrorCode:
    """Structured error codes for identifying failure points."""

    # Validation
    VALIDATION_ERROR = "VALIDATION_ERROR"

    # Agent errors
    INTENT_CLASSIFICATION_ERROR = "INTENT_CLASSIFICATION_ERROR"
    CODER_AGENT_ERROR = "CODER_AGENT_ERROR"
    REVIEW_AGENT_ERROR = "REVIEW_AGENT_ERROR"
    RESEARCHER_AGENT_ERROR = "RESEARCHER_AGENT_ERROR"
    ORCHESTRATOR_ERROR = "ORCHESTRATOR_ERROR"

    # LLM errors
    LLM_INITIALIZATION_ERROR = "LLM_INITIALIZATION_ERROR"
    LLM_INVOCATION_ERROR = "LLM_INVOCATION_ERROR"

    # Service / Router errors
    SERVICE_ERROR = "SERVICE_ERROR"
    ROUTER_ERROR = "ROUTER_ERROR"

    # Database errors
    DB_CONNECTION_FAIL = "DB_CONNECTION_FAIL"
    DB_OPERATION_ERROR = "DB_OPERATION_ERROR"

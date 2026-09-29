"""
Request model for the Multi-Agent Code Pipeline endpoint.
"""
from pydantic import BaseModel, Field


class CodeRequest(BaseModel):
    """Represents the incoming user request containing a natural language query."""

    user_query: str = Field(
        ...,
        description="Natural language prompt from the user — the LLM determines whether to code, review, or research.",
        min_length=1
    )

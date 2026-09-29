"""
Custom application exception for standardized error handling
across the Multi-Agent Code Pipeline API layer.
"""
import uuid
from typing import List, Optional
from models.api_response_dto import APIResponse, Error


class CustomAppException(Exception):
    """
    Raises a structured application exception that maps directly
    to a standardized API response with error codes and HTTP status.
    """

    def __init__(
        self,
        message: str,
        code: str,
        status_code: int,
        errors: Optional[List[Error]] = None
    ):
        """
        Initializes the exception with a message, error code, HTTP status,
        and an optional list of structured errors.
        """
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.errors = errors or [Error(code=code, message=message)]
        self.request_id = str(uuid.uuid4())

    def to_api_response(self) -> APIResponse:
        """Converts the exception into a standardized APIResponse object."""
        return APIResponse(
            data=None,
            errors=self.errors,
            code=self.status_code
        )

    def __str__(self)-> str:
        """Returns a traceable string representation of the exception."""
        first_err = self.errors[0]
        return f"[{self.request_id}] {first_err.message} (Code: {first_err.code}, HTTP: {self.status_code})"

    @classmethod
    def from_errors(cls, errors: List[Error], status_code: int):
        """
        Creates a CustomAppException from a list of structured Error objects.
        Uses the first error as the top-level message and code.
        """
        if not errors:
            return cls(
                message="Unknown error occurred",
                code="UNKNOWN_ERROR",
                status_code=status_code
            )
        first_error = errors[0]
        return cls(
            message=first_error.message,
            code=first_error.code,
            status_code=status_code,
            errors=errors
        )

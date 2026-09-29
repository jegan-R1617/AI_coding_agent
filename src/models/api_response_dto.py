"""
Standardized Data Transfer Objects for API responses.
Ensures consistent response structure across all endpoints.
"""
import uuid
from typing import List, Any, Optional
from datetime import datetime, timezone


class Error:
    """Represents a single structured error with a code and message."""

    def __init__(self, code: str, message: str):
        """Initializes an error with a code and human-readable message."""
        self.code = code
        self.message = message

    def to_dict(self) -> dict:
        """Serializes the error to a dictionary for JSON responses."""
        return {
            "code": self.code,
            "message": self.message
        }


class APIResponse:
    """
    Encapsulates a standardized API response for both success and error scenarios.
    Auto-generates an appropriate message based on errors present.
    """

    def __init__(
        self,
        data: Any = None,
        errors: Optional[List[Error]] = None,
        code: Optional[int] = None,
        message: Optional[str] = None
    ):
        """
        Initializes the API response with data, errors, status code, and message.
        Message is auto-generated if not provided based on error presence.
        """
        self.data = data or []
        self.errors = errors or []
        self.code = code or 200
        self.request_id = str(uuid.uuid4())
        self.timestamp = datetime.now(timezone.utc).isoformat()

        if message is not None:
            self.message = message
        elif not self.errors:
            self.message = "Success"
        elif len(self.errors) == 1:
            self.message = self.errors[0].message
        else:
            self.message = "Something went wrong."

    def to_dict(self) -> dict:
        """Serializes the full API response to a dictionary for JSON output."""
        return {
            "data": self.data,
            "errors": [error.to_dict() for error in self.errors] if self.errors else [],
            "status_code": self.code,
            "request_id": self.request_id,
            "timestamp": self.timestamp,
            "message": self.message
        }

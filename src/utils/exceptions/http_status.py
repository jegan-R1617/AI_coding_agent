"""
HTTP status codes used across the Multi-Agent Code Pipeline.
Only includes codes that are actually used in this application.
"""


class HttpStatusCode:
    """Standard HTTP status codes relevant to this application."""

    OK = 200
    BAD_REQUEST = 400
    UNPROCESSABLE_ENTITY = 422
    INTERNAL_SERVER_ERROR = 500
    SERVICE_UNAVAILABLE = 503

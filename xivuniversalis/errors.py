class UniversalisError(Exception):
    """Base class for all Universalis exceptions."""
    ...


class UniversalisServerError(UniversalisError):
    """Exception raised when Universalis returns a server error or an invalid json response."""
    ...
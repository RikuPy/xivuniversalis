__all__ = ["UniversalisError", "InvalidServerError", "InvalidParametersError", "UniversalisServerError"]


class UniversalisError(Exception):
    """Base class for all Universalis exceptions."""

    ...


class InvalidServerError(UniversalisError):
    """Exception raised when an invalid world, datacenter or region is provided to the API."""

    ...


class InvalidParametersError(UniversalisError):
    """Exception raised when an invalid parameter is provided to the API."""

    ...


class UniversalisServerError(UniversalisError):
    """Exception raised when Universalis returns an internal server error."""

    ...

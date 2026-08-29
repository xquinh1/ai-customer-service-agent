class AppError(Exception):
    """Base class for all application-level errors.

    Route handlers stay thin: services raise typed exceptions like
    ``NotFoundError``, and FastAPI converts them to HTTP responses via
    global exception handlers registered in ``main.py``.
    """


class NotFoundError(AppError):
    """Raised when a requested resource does not exist."""

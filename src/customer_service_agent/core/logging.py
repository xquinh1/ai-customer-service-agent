import logging

_configured = False

LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def setup_logging(level: str = "INFO") -> None:
    """Configure the root logger once with a consistent format.

    Uvicorn configures its own loggers (``uvicorn``, ``uvicorn.access``)
    with ``propagate=False``, so adding a handler on the root logger
    does not duplicate uvicorn output.
    """
    global _configured

    if _configured:
        return

    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT))

    root = logging.getLogger()
    root.setLevel(level.upper())
    root.addHandler(handler)

    _configured = True


def get_logger(name: str) -> logging.Logger:
    """Return a logger for ``name``, configuring logging on first use.

    ``name`` should be the module's ``__name__`` so log records show
    which module produced them.
    """
    setup_logging()
    return logging.getLogger(name)

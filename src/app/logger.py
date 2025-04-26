import logging.config

import structlog

logger_app = structlog.getLogger()


def logger_init(log_file: str = ""):
    if log_file != "":
        logging.config.dictConfig(
            {
                "version": 1,
                "disable_existing_loggers": False,
                "handlers": {
                    "default": {
                        "level": "DEBUG",
                        "class": "logging.StreamHandler",
                    },
                    "file": {
                        "level": "DEBUG",
                        "class": "logging.handlers.WatchedFileHandler",
                        "filename": f"{log_file}",
                    },
                },
                "loggers": {
                    "": {
                        "handlers": ["default", "file"],
                        "level": "DEBUG",
                        "propagate": True,
                    },
                },
            }
        )

    structlog.configure(
        processors=[
            structlog.processors.add_log_level,
            structlog.processors.ExceptionRenderer(),
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S"),
            structlog.processors.EventRenamer("msg"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.dict_tracebacks,
            structlog.processors.JSONRenderer(),
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

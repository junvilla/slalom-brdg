import logging
import logging.config
import os
import datetime

# Define the default logging configuration
now_str = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s|%(levelname)s|%(name)s|%(message)s",
        },
        "console": {
            "format": "[%(asctime)s][%(levelname)s][%(name)s] %(message)s",
            "datefmt": "%H:%M:%S",
        },
    },
    "handlers": {
        "file": {
            "class": "logging.FileHandler",
            "filename": ("./LOG/" + "Tableau.Migration-" + now_str + ".log"),
            "formatter": "default",
            "level": logging.DEBUG,
        },
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "console",
            "level": logging.INFO,
        },
    },
    "root": {
        "handlers": ["file", "console"],
        "level": logging.DEBUG,
    },
}


def setup_logging():
    # Check for the logging directory
    if not os.path.exists("LOG"):
        os.makedirs("LOG")

    # Load the logging configuration
    logging.config.dictConfig(LOGGING_CONFIG)


# Initialize logging
setup_logging()

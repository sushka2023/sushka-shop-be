import logging
import os
import sys


def setup_logging():
    log_directory = "logs"
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)

    if sys.stdout.encoding != "utf-8":
        sys.stdout = open(sys.stdout.fileno(), mode="w", encoding="utf-8", buffering=1)
    if sys.stderr.encoding != "utf-8":
        sys.stderr = open(sys.stderr.fileno(), mode="w", encoding="utf-8", buffering=1)

    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s - %(asctime)s - %(name)s - %(message)s",
        datefmt="%d-%m-%Y %H:%M:%S",
        handlers=[
            logging.FileHandler("logs/app.log", encoding="utf-8"),
            logging.StreamHandler(sys.stdout)
        ]
    )


logger = logging.getLogger(__name__)


logger.info("This is logged by the global logger")

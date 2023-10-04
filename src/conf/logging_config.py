import logging
import sys


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s - %(asctime)s - %(name)s - %(message)s",
        datefmt="%d-%m-%Y %H:%M:%S",
        handlers=[
            logging.FileHandler("logs/app.log"),
            logging.StreamHandler(sys.stdout)
        ]
    )


logger = logging.getLogger(__name__)


logger.info("This is logged by the global logger")

import logging
from definitions import LOG_FILE

logging.basicConfig(
        format = "%(asctime)s | %(levelname)s: %(message)s",
        filename = LOG_FILE,
        level = logging.DEBUG
)

logger = logging.getLogger('Logger')
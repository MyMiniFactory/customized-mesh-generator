import sys
import logging

logging.basicConfig(
	stream=sys.stdout,
	format="%(asctime)s | %(levelname)s: %(message)s",
	level=logging.INFO
)

logger = logging.getLogger('Logger')
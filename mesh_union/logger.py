from os import path
import logging
from definitions import LOG_FILE

log_format = "%(asctime)s | %(levelname)s: %(message)s"

def get_logging_config(log_file, level):
	if path.exists(log_file):
		return {
			'filename': log_file,
			'format': log_format,
			'level': level, 
		}
	else:
		from sys import stdout
		return {
			'stream': stdout,
			'format': log_format,
			'level': level
		}

logging.basicConfig(**get_logging_config(LOG_FILE, logging.DEBUG))

logger = logging.getLogger('Logger')
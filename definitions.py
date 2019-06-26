from os import path

ROOT_DIR = path.dirname(path.abspath(__file__))

MODELS_DIR = path.join(ROOT_DIR, 'models')
LOG_FILE = path.join(ROOT_DIR, 'data/logs/logs')
OUT_DIR = path.join(ROOT_DIR, 'data/out')
# LOG_BINDINGS = path.join(ROOT_DIR, 'data/logs/bindings')
# LOG_ERRORS = path.join(ROOT_DIR, 'data/logs/errors')
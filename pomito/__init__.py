"""Pomito package initialization."""
# Init module
# TODO:
# - Set configuration parameters
# - Load any available plugisn
# - Load user data?

import logging

logger = logging.getLogger('pomito')
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)-6s: %(threadName)s: %(name)s: [%(levelname)s] %(message)s'))
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

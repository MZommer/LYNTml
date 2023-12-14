import logging

logger = logging.getLogger('LyN')

logger.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger.setFormatter(formatter)

def toggle_level():
    if logger.level == logging.DEBUG:
        logger.setLevel(logging.INFO)
    else:
        logger.setLevel(logging.DEBUG)

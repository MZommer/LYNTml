import logging

logger = logging.getLogger('LyN')

logger.setLevel(logging.INFO)

# Create a handler
handler = logging.StreamHandler()

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Set the formatter to the handler, not the logger
handler.setFormatter(formatter)

# Add the handler to the logger
logger.addHandler(handler)

def toggle_level():
    if logger.level == logging.DEBUG:
        logger.setLevel(logging.INFO)
    else:
        logger.setLevel(logging.DEBUG)

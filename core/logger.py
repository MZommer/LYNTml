import logging

logger = logging.getLogger("LyN")

logger.setLevel(logging.DEBUG)

handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


def toggle_level() -> None:
    if logger.level == logging.DEBUG:
        logger.setLevel(logging.INFO)
    else:
        logger.setLevel(logging.DEBUG)

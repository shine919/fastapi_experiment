import logging

from core.config import settings


def get_logger(level: str = settings.level):
    logging.basicConfig(
        level=level,
        datefmt="%Y-%m-%d %H:%M:%S",
        format="[%(asctime)s.%(msec)03d] %(module)10s:%(lineno)-3d %(levelname)-7s - %(message)s",
    )

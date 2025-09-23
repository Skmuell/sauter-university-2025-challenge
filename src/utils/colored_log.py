import colorlog
from dotenv import load_dotenv
import logging
import os
from pathlib import Path
from typing import cast

load_dotenv(override=True)

_log_level_str = os.getenv('log_level', 'INFO').upper()
_log_level = logging._nameToLevel.get(_log_level_str, logging.INFO)


class CustomRelativePathFilter(logging.Filter):
    def __init__(self, project_root: Path):
        super().__init__()
        self.project_root = Path(project_root).resolve()

    def filter(self, record):
        try:
            rel_path = Path(record.pathname).resolve().relative_to(self.project_root)
            record.relpath = str(rel_path).replace("\\", "/")
        except ValueError:
            record.relpath = record.pathname
        return True


_formatter = colorlog.ColoredFormatter(
    '[%(log_color)s%(levelname)s%(reset)s] '
    '[%(purple)s%(asctime)s%(reset)s] '
    '{{%(light_red)s%(relpath)s%(reset)s:%(light_cyan)s%(lineno)d%(reset)s}} '
    '%(light_black)s>%(reset)s> %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    log_colors={
        "DEBUG": "bold_blue",
        "INFO": "light_green",
        "WARNING": "yellow",
        "ERROR": "red",
        "CRITICAL": "red",
    },
    reset=True,
    style='%'
)


def create_logger(module_name: str) -> logging.Logger:
    handler = logging.StreamHandler()
    handler.setFormatter(_formatter)

    logger = logging.getLogger(module_name)
    logger.handlers.clear()
    logger.propagate = False
    logger.addHandler(handler)

    project_root = Path(__file__).parent.parent  # ajuste conforme sua estrutura
    handler.addFilter(CustomRelativePathFilter(project_root))

    logger.setLevel(_log_level)
    return logger
import logging
import os

from interviews.core.exceptions import BrockenPathExeption, InjectExeption


async def validate_path(file_path: str) -> str:
    if "/" not in file_path:
        raise BrockenPathExeption
    full_path = os.path.join("static", file_path)
    full_path = os.path.normpath(full_path)
    if os.path.commonpath([full_path, "static"]) != "static":
        logging.error("Warning! Attempting to inject.")
        raise InjectExeption
    return full_path

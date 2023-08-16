import logging
from importlib.metadata import PackageNotFoundError, version

logger = logging.getLogger(__name__)

try:
    __version__ = version(__name__)
except PackageNotFoundError:  # pragma: no cover
    logger.debug("Unable to read version, not installed as package")

import logging
import os

from flask import Flask
from prometheus_flask_exporter import PrometheusMetrics
from prometheus_flask_exporter.multiprocess import GunicornInternalPrometheusMetrics

from . import __version__ as APP_VERSION

logger = logging.getLogger(__name__)

metrics: PrometheusMetrics

if os.getenv("IS_GUNICORN"):
    metrics = GunicornInternalPrometheusMetrics.for_app_factory()
else:
    metrics = PrometheusMetrics.for_app_factory()

try:
    metrics.info("app_info", "Application info", version=APP_VERSION)
except ValueError:
    logger.debug("Skipping app_info metric duplicate")


def init_metrics(app: Flask) -> None:
    metrics.init_app(app)

from prometheus_flask_exporter.multiprocess import GunicornPrometheusMetrics

from . import __version__ as APP_VERSION

metrics = GunicornPrometheusMetrics.for_app_factory()
# static information as metric
metrics.info("app_info", "Application info", version=APP_VERSION)

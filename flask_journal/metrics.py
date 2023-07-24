import os

from prometheus_flask_exporter.multiprocess import GunicornPrometheusMetrics

metrics = GunicornPrometheusMetrics.for_app_factory()
# static information as metric
metrics.info("app_info", "Application info", version=os.getenv("APP_VERSION"))

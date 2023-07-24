import os

from gunicorn.arbiter import Arbiter
from gunicorn.workers.base import Worker
from prometheus_flask_exporter.multiprocess import GunicornPrometheusMetrics

os.environ["IS_GUNICORN"] = "true"


def when_ready(server: Arbiter) -> None:
    GunicornPrometheusMetrics.start_http_server_when_ready(9191)


def child_exit(server: Arbiter, worker: Worker) -> None:
    GunicornPrometheusMetrics.mark_process_dead_on_child_exit(worker.pid)

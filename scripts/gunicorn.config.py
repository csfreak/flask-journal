import os

from gunicorn.arbiter import Arbiter
from gunicorn.workers.base import Worker
from prometheus_flask_exporter.multiprocess import GunicornInternalPrometheusMetrics

os.environ["IS_GUNICORN"] = "true"


def child_exit(server: Arbiter, worker: Worker) -> None:
    GunicornInternalPrometheusMetrics.mark_process_dead_on_child_exit(worker.pid)


worker_connections: int = 10
max_requests: int = 100
max_requests_jitter: int = 10
proc_name: str = "flask_journal"

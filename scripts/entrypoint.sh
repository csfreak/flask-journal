#!/bin/sh
cd /app
source .venv/bin/activate

if [ $# -ne 0 ];  then
    exec $@
fi

GUNICORN_CMD_ARGS="--chdir /app  --threads ${WORKER_THREADS}  --config gunicorn.config.py ${EXTRA_ARGS}"

PROMETHEUS_MULTIPROC_DIR=${PROMETHEUS_MULTIPROC_DIR:-/prom}
if [ -e ${PROMETHEUS_MULTIPROC_DIR} ]; then
    rm -rf ${PROMETHEUS_MULTIPROC_DIR}
fi
mkdir -p ${PROMETHEUS_MULTIPROC_DIR}
export PROMETHEUS_MULTIPROC_DIR


if [ ${DEBUG} ]; then
    GUNICORN_CMD_ARGS="${GUNICORN_CMD_ARGS} --error-logfile -  --log-level LEVEL debug"
    export FLASK_DEBUG=1
    export FLASK_JOURNAL_DEBUG=1
fi

export GUNICORN_CMD_ARGS
exec gunicorn 'flask_journal.app:create_app()'
FROM python:3.12-alpine as builder

WORKDIR /app
COPY dist/*.whl /app/dist/ 

RUN python3 -mvenv /app/.venv && \
    source /app/.venv/bin/activate && \
    pip3 install --find-links=dist/ 'flask-journal[deploy]'  && \
    rm -rf /app/dist

FROM python:3.12-alpine 

WORKDIR /app
COPY --from=builder /app /app
COPY scripts/entrypoint.sh scripts/gunicorn.config.py /app/
COPY migrations /app/migrations
ENV FLASK_APP=flask_journal.app
ENV PORT=5000
ENV WORKER_THREADS=5
ENTRYPOINT ["/app/entrypoint.sh"]
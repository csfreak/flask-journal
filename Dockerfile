FROM python:3.11-alpine as builder

WORKDIR /app
COPY requirements.txt /

RUN python3 -mvenv /app/.venv && \
    source /app/.venv/bin/activate && \
    pip3 install -r /requirements.txt && \
    pip3 install gunicorn

COPY flask_journal migrations /app/

FROM python:3.11-alpine 
ARG APP_VERSION

WORKDIR /app
COPY --from=builder /app /app
COPY scripts/entrypoint.sh scripts/gunicorn.config.py /app/
ENV FLASK_APP=/app/flask_journal/app.py
ENV APP_VERSION=${APP_VERSION}
ENV ALEMBIC_REVISION=head
ENV PORT=5000
ENV WORKER_THREADS=5
ENTRYPOINT ["/app/entrypoint.sh"]
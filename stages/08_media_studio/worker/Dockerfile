FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DREAMCO_WORKER_HOST=0.0.0.0 \
    DREAMCO_WORKER_PORT=8080 \
    DREAMCO_MEDIA_SPOOL=/var/lib/dreamco-media

WORKDIR /app
RUN useradd --system --uid 10001 --create-home dreamco \
    && mkdir -p /var/lib/dreamco-media \
    && chown -R dreamco:dreamco /app /var/lib/dreamco-media

COPY --chown=dreamco:dreamco stages/08_media_studio/director.py /app/director.py
COPY --chown=dreamco:dreamco stages/08_media_studio/worker/server.py /app/server.py

USER 10001:10001
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8080/healthz', timeout=2).read()"

CMD ["python", "/app/server.py"]

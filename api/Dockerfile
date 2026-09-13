# Build context is the repo root (see docker-compose.yml) since this needs
# both src/socpipeline and api/.
FROM python:3.12.7-slim-bookworm

WORKDIR /app

# Install dependencies first so this layer stays cached across code changes.
COPY requirements.txt requirements-api.txt ./
RUN pip install --no-cache-dir -r requirements-api.txt

COPY src/ src/
COPY api/ api/

# Fixed UID/GID (not a system user picked at build time) so the container's
# file ownership is reproducible across rebuilds.
RUN groupadd --gid 10001 appuser \
    && useradd --uid 10001 --gid appuser --no-create-home --shell /usr/sbin/nologin appuser \
    && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --retries=3 --start-period=5s \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/api/health', timeout=3)" || exit 1

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]

# syntax=docker/dockerfile:1
FROM python:3.12-slim-bookworm@sha256:34386ef0cb081344d7ec1c103ba398e6e9f64e9ab3a1509accc92a4e24a07258 AS build
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=true POETRY_NO_INTERACTION=1
WORKDIR /app
RUN pip install poetry==2.3.2
COPY pyproject.toml poetry.lock ./
RUN poetry install --only main --no-root
COPY . .
RUN DJANGO_SECRET_KEY=build-only-not-a-deployment-secret-0000000000000000000000000000 \
    POSTGRES_DB=build POSTGRES_USER=build POSTGRES_PASSWORD=build \
    .venv/bin/python manage.py collectstatic --noinput --settings=config.settings.production

FROM python:3.12-slim-bookworm@sha256:34386ef0cb081344d7ec1c103ba398e6e9f64e9ab3a1509accc92a4e24a07258 AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=config.settings.production PATH="/app/.venv/bin:$PATH"
RUN groupadd --gid 10001 kuylab && useradd --uid 10001 --gid kuylab --no-create-home kuylab \
    && mkdir -p /data/media && chown kuylab:kuylab /data/media
WORKDIR /app
COPY --from=build --chown=kuylab:kuylab /app /app
USER 10001:10001
EXPOSE 8000
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "2", "--threads", "2", "--timeout", "60", "--graceful-timeout", "30", "--max-requests", "1000", "--max-requests-jitter", "100", "--access-logfile", "-", "--error-logfile", "-"]

ARG PY_VERSION=3.10
FROM python:${PY_VERSION}-slim-bullseye AS base

ENV LANG "C.UTF-8"
ENV SHELL "/bin/bash"
ENV TZ "UTC"
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

RUN apt-get update -y && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    ; rm -rf /var/lib/apt/lists/*

WORKDIR /usr/app/evaluation_agent/
COPY ./ ./

RUN pip install poetry==1.2.2

# Build target for CI and local development
FROM base AS dev
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

# Build target for staging and prod
FROM base AS prod

RUN poetry config virtualenvs.create false \
    && poetry install --only main --no-interaction --no-ansi

CMD poetry run ddtrace-run uvicorn huma_signals.api.main:app --reload --host "0.0.0.0"

# syntax=docker/dockerfile:1
FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# System deps (build essentials not needed for this project)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Copy project files
COPY pyproject.toml README.md /app/
COPY src /app/src

# Install only runtime deps
RUN pip install --upgrade pip && \
    pip install .

EXPOSE 8000

CMD ["uvicorn", "python_mastery_portfolio.api:app", "--host", "0.0.0.0", "--port", "8000"]

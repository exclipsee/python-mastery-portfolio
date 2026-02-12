FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential curl \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -m app

WORKDIR /app

# Copy project metadata and sources (layer caching friendly)
COPY pyproject.toml pyproject.toml
COPY src/ src/

RUN pip install --upgrade pip setuptools wheel
RUN pip install .[api]

USER app

EXPOSE 8000

CMD ["uvicorn", "python_mastery_portfolio.api:app", "--host", "0.0.0.0", "--port", "8000"]

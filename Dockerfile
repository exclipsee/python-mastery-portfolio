FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install build deps and runtime extras
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy only what we need for a pip install to leverage layer caching
COPY pyproject.toml pyproject.toml
COPY src/ src/

# Install package with FastAPI extras so the API can run
RUN pip install --upgrade pip
RUN pip install .[api]

EXPOSE 8000

CMD ["uvicorn", "python_mastery_portfolio.api:app", "--host", "0.0.0.0", "--port", "8000"]

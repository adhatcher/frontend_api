# ---------- builder ----------
FROM python:3.12-slim AS builder

WORKDIR /app

# Copy dependency manifests first for better build caching
COPY pyproject.toml poetry.lock ./

RUN pip install --no-cache-dir poetry \
    && poetry config virtualenvs.create false \
    && poetry install --only main --no-root

COPY ./src/ .

# ---------- runtime ----------
FROM python:3.12-slim

WORKDIR /app

# Add metadata
LABEL maintainer="Aaron Hatcher <aaron@aaronhatcher.com>"
LABEL description="Flask application with configurable host and port using environment variables."

RUN mkdir /logs && chmod 775 /logs

# Copy installed deps and app source
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /app /app

# Set default environment variables (can be overridden at runtime)
ENV FLASK_HOST=0.0.0.0
ENV FLASK_PORT=8080
ENV API_HOST=backend
ENV API_PORT=7070
ENV API_URL=backend/random_phrase

# Expose the port (not required but good practice)
EXPOSE ${FLASK_PORT}

# Command to run the application
CMD ["python", "frontend_app.py"]

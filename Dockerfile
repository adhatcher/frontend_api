# Use the official Python image as a base image
FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    # build-essential \
    # curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Set the working directory in the container
WORKDIR /app

# Add metadata
LABEL maintainer="Aaron Hatcher <aaron@aaronhatcher.com>"
LABEL description="Flask application with configurable host and port using environment variables."

# Copy the application files
COPY . .

# Install dependencies
RUN mkdir /logs && chmod 777 /logs && \
    pip install --no-cache-dir poetry && \
    poetry install --only main --no-root

# Set default environment variables (can be overridden at runtime)
ENV FLASK_HOST=0.0.0.0
ENV FLASK_PORT=8080
ENV API_HOST=backend
ENV API_PORT=7070
ENV API_URL=backend/random_phrase

# Expose the port (not required but good practice)
EXPOSE ${FLASK_PORT}

# Command to run the application
CMD ["poetry", "run", "python", "frontend_app.py"]
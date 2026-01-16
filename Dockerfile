# Use the official Python image as a base image
FROM python:3.12-slim

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
ENV FLASK_PORT=6060
ENV API_HOST=backend
ENV API_PORT=7070

# Expose the port (not required but good practice)
EXPOSE ${FLASK_PORT}

# Command to run the application
CMD ["poetry", "run", "python", "frontend_app.py"]
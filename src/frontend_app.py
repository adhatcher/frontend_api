"""Flask frontend for retrieving and rendering phrases from a backend API."""

import logging
import os
import time
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
from urllib.parse import urlunparse

import requests
from flask import Flask, Response, jsonify, render_template
from prometheus_client import REGISTRY, Counter, Histogram, generate_latest
from requests import RequestException


BASE_DIR = Path(__file__).resolve().parents[1]
app = Flask(
    __name__,
    template_folder=str(BASE_DIR / "templates"),
    static_folder=str(BASE_DIR / "static"),
)

def _as_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _build_api_url() -> str:
    explicit_url = os.getenv("API_URL", "").strip()
    if explicit_url.startswith(("http://", "https://")):
        return explicit_url

    host = os.getenv("API_HOST", "backend")
    port = os.getenv("API_PORT", "7070")
    path = explicit_url or os.getenv("API_PATH", "random_phrase")
    normalized_path = "/" + path.strip("/")
    return urlunparse(("http", f"{host}:{port}", normalized_path, "", "", ""))


API_URL = _build_api_url()
REQUEST_TIMEOUT_SECONDS = float(os.getenv("REQUEST_TIMEOUT_SECONDS", "3.0"))
FLASK_HOST = os.getenv("FLASK_HOST", "0.0.0.0")
FLASK_PORT = int(os.getenv("FLASK_PORT", "8080"))
FLASK_DEBUG = _as_bool(os.getenv("FLASK_DEBUG"), default=False)

# Prometheus metrics
REQUEST_COUNT = Counter("frontend_request_count", "Total number of requests")
PHRASE_REQUEST_LATENCY = Histogram(
    "phrase_request_latency_seconds", "Time taken for a request to the Flask API"
)
RENDER_LATENCY = Histogram(
    "render_latency_seconds", "Time taken to render the phrase view"
)
FAILED_REQUESTS = Counter("frontend_failed_requests", "Number of failed requests")
PHRASE_COUNTER = Counter("frontend_phrase_counter", "Count of each phrase", ["phrase"])

LOG_DIR = os.getenv("LOG_DIR", "logs")
handler: logging.Handler
try:
    os.makedirs(LOG_DIR, exist_ok=True)
    log_file = os.path.join(LOG_DIR, "frontend_app.log")
    handler = TimedRotatingFileHandler(log_file, when="D", interval=1, backupCount=4)
except OSError:
    # Fall back to stderr if filesystem paths are not writable.
    handler = logging.StreamHandler()

handler.setLevel(logging.INFO)

# Set log format
formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)
handler.setFormatter(formatter)

# Attach handler to Flask app logger
app.logger.addHandler(handler)
app.logger.setLevel(logging.INFO)

# Redirect Werkzeug logs (Flask's built-in server logs)
werkzeug_logger = logging.getLogger("werkzeug")
werkzeug_logger.setLevel(logging.INFO)
werkzeug_logger.addHandler(handler)

session = requests.Session()


def _fetch_phrase_data() -> dict[str, float | str | None]:
    start_time = time.perf_counter()
    response = session.get(API_URL, timeout=REQUEST_TIMEOUT_SECONDS)
    response.raise_for_status()
    payload = response.json()
    phrase = str(payload.get("phrase", "No phrase returned"))
    selection_time = payload.get("selection_time")
    total_time = round(time.perf_counter() - start_time, 4)
    PHRASE_COUNTER.labels(phrase=phrase).inc()
    return {
        "phrase": phrase,
        "selection_time": selection_time,
        "total_time": total_time,
    }


@app.after_request
def _apply_security_headers(response: Response) -> Response:
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; img-src 'self' data:; style-src 'self'; "
        "script-src 'self'; base-uri 'none'; form-action 'self'"
    )
    return response


def _render_phrase_page() -> tuple[str, int]:
    try:
        app.logger.info("Fetching phrase from backend endpoint: %s", API_URL)
        phrase_data = _fetch_phrase_data()
        return render_template("phrase.html", **phrase_data), 200
    except (RequestException, ValueError) as exc:
        FAILED_REQUESTS.inc()
        app.logger.warning("Failed to fetch phrase: %s", exc)
        return (
            render_template(
                "phrase.html",
                phrase="Unable to fetch phrase right now.",
                selection_time=None,
                total_time=None,
                error="Backend service unavailable. Please try again.",
            ),
            502,
        )


@app.route("/metrics", methods=["GET"])
def metrics():
    """Expose Prometheus metrics for scraping."""
    return Response(generate_latest(REGISTRY), mimetype="text/plain")


@app.route("/healthz", methods=["GET"])
def healthz():
    """Return readiness status for health checks."""
    return jsonify({"status": "ok"}), 200


@app.route("/get_phrase", methods=["GET"])
@REQUEST_COUNT.count_exceptions()
@PHRASE_REQUEST_LATENCY.time()
def get_phrase():
    """Render a page with the latest phrase from the backend API."""
    return _render_phrase_page()


@app.route("/", methods=["GET"])
@RENDER_LATENCY.time()
def home():
    """Render the landing page."""
    return render_template("index.html"), 200


if __name__ == "__main__":
    app.run(debug=FLASK_DEBUG, host=FLASK_HOST, port=FLASK_PORT)

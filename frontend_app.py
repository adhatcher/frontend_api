from flask import Flask, jsonify, render_template, Response
import requests
import time
import os
from prometheus_client import Counter, Histogram, generate_latest, REGISTRY
import logging
from logging.handlers import TimedRotatingFileHandler


app = Flask(__name__)

# Get the API host and port from environment variables (default to zeus.local:6060)
API_HOST = os.getenv("API_HOST", "zeus.local")
API_PORT = os.getenv("API_PORT", "6061")
API_URL = f"http://{API_HOST}:{API_PORT}/random_phrase"

# Prometheus metrics
REQUEST_COUNT = Counter('frontend_request_count', 'Total number of requests')
PHRASE_REQUEST_LATENCY = Histogram('phrase_request_latency_seconds', 'Time taken for a request to the Flask API')
RENDER_LATENCY = Histogram('render_latency_seconds', 'Time taken to render the phrase')
FAILED_REQUESTS = Counter('frontend_failed_requests', 'Number of failed requests')
PHRASE_COUNTER = Counter('frontend_phrase_counter', 'Count of each phrase', ['phrase'])

log_dir = "/logs"
os.makedirs(log_dir, exist_ok=True)

# Configure log file handler
log_file = os.path.join(log_dir, "frontend_app.log")
handler = TimedRotatingFileHandler(log_file, when="D", interval=1, backupCount=4)
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
werkzeug_logger.setLevel(logging.DEBUG)
werkzeug_logger.addHandler(handler)

@app.route('/metrics', methods=['GET'])
def metrics():
    return Response(generate_latest(REGISTRY), mimetype='text/plain')

@app.route('/get_phrase', methods=['GET'])
@REQUEST_COUNT.count_exceptions()
@PHRASE_REQUEST_LATENCY.time()
def get_phrase():
    try:
        app.logger.info("/get_phrase called.")
        start_time = time.time()
        response = requests.get(API_URL)
        if response.status_code != 200:
            raise Exception(f'Failed to get phrase: {response.status_code}')
        data = response.json()
        phrase = data.get('phrase', 'No phrase returned')
        PHRASE_COUNTER.labels(phrase=phrase).inc()
        end_time = time.time()

        return render_template('phrase.html', phrase=phrase, selection_time=data.get('selection_time'), total_time=end_time - start_time)
    except Exception as e:
        FAILED_REQUESTS.inc()
        return jsonify({'error': str(e)}), 500

@app.route('/', methods=['GET'])
@RENDER_LATENCY.time()
def home():
    try:
        app.logger.info("/get_phrase called.")
        start_time = time.time()
        response = requests.get(API_URL)
        if response.status_code != 200:
            raise Exception(f'Failed to get phrase: {response.status_code}')
        data = response.json()
        phrase = data.get('phrase', 'No phrase returned')
        PHRASE_COUNTER.labels(phrase=phrase).inc()
        end_time = time.time()
        app.logger.info("/get_phrase successful.")
        return render_template('phrase.html', phrase=phrase, selection_time=data.get('selection_time'), total_time=end_time - start_time)
    except Exception as e:
        FAILED_REQUESTS.inc()
        app.logger.warn("/get_phrase failed.")
        return jsonify({'error': str(e)}), 500
    

if __name__ == '__main__':
    # Get Flask app host and port from environment variables
    FLASK_HOST = os.getenv("FLASK_HOST", "0.0.0.0")
    FLASK_PORT = int(os.getenv("FLASK_PORT", "6060"))
    
    app.run(debug=True, host=FLASK_HOST, port=FLASK_PORT)
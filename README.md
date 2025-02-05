# frontend_app
Variables: 
API_HOST: host the random_phrase_api is running.
API_PORT: port the API is running on on the API_HOST
FLASK_PORT: Port to run this API on.

## Run with the following command:
```bash
docker run -d -p 8080:8080 \
    -e FLASK_HOST=0.0.0.0 \
    -e FLASK_PORT=8080 \
    -e API_HOST=my-api-server.com \
    -e API_PORT=7070 \
    ahatcher/frontend:v1
```


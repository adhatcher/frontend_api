# frontend_app

Flask frontend service that fetches random phrases from a backend API and renders a web UI.

## Requirements

- Python `3.12+`
- Poetry `2.x`
- Backend phrase API service (example: `adhatcher/random-phrase`)

## Environment Variables

- `FLASK_HOST`: frontend bind host (default: `0.0.0.0`)
- `FLASK_PORT`: frontend port (default: `8080`)
- `FLASK_DEBUG`: set `true` only for local debugging (default: `false`)
- `LOG_DIR`: directory for frontend logs (default: `logs`)
- `API_HOST`: backend host (default: `backend`)
- `API_PORT`: backend port (default: `7070`)
- `API_PATH`: backend path when `API_URL` is not fully qualified (default: `random_phrase`)
- `API_URL`: full backend URL override (example: `https://api.example.com/random_phrase`)
- `REQUEST_TIMEOUT_SECONDS`: backend request timeout (default: `3.0`)

## Local Development

Install dependencies:

```bash
make install
```

Run the app locally:

```bash
make run
```

## Docker Run

Create a shared network:

```bash
docker network create app-net
```

Run backend (example):

```bash
docker run -d --rm --name backend \
  --network app-net \
  -p 7070:7070 \
  -h backend \
  -e FLASK_PORT=7070 \
  -e API_PORT=7070 \
  <backend-image>
```

Run frontend:

```bash
docker run -d --rm --name frontend \
  --network app-net \
  -p 8080:8080 \
  -e FLASK_HOST=0.0.0.0 \
  -e FLASK_PORT=8080 \
  -e API_HOST=backend \
  -e API_PORT=7070 \
  <frontend-image>
```

## Endpoints

- `/` - landing page
- `/get_phrase` - fetch and render phrase
- `/healthz` - health endpoint
- `/metrics` - Prometheus metrics endpoint

## Testing and Coverage

Run tests:

```bash
make test
```

Run coverage and output reports:

```bash
make cover
```

Coverage artifacts are written to:

- `reports/xunit.xml`
- `reports/coverage.xml`

## Developer Commands

- `make install` - install dependencies
- `make run` - run app locally
- `make test` - run pytest
- `make cover` - run pytest + coverage reports
- `make lint` - run Ruff lint checks
- `make format` - format code with Ruff
- `make ci` - run clean + install + test + cover + package step

Note: package build is skipped automatically when `package-mode = false`.

## Security Remediation Workflow

This repo includes the GitHub Actions workflow `Security Remediation Agent`.

Workflow inputs:

- `severity_threshold`: `high` or `critical`
- `dry_run`: `true` or `false`
- `max_alerts`: max alerts to process

Recommended secret:

- `DEPENDABOT_ALERTS_TOKEN` (fine-grained PAT with `Dependabot alerts: Read-only`)

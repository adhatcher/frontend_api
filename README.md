# frontend_app

## Prerequisites

- Create a docker network called app-net `docker network create app-net`
- [https://github.com/adhatcher/random-phrase](https://github.com/adhatcher/random-phrase]) up and running with the following docker configuration:
  - `docker run -d --rm --name backend --network app-net -p 7070:7070 -h backend -e FLASK_PORT=7070 -e API_PORT=7070 <container_image>`

## Variables

- **API_HOST**: host the random_phrase_api is running.
- **API_PORT**: port the API is running on on the API_HOST
- **FLASK_PORT**: Port to run this API on.

## Run with the following command

```bash
docker run -d --rm -p 8080:8080 \
    -e FLASK_HOST=0.0.0.0 \
    -e FLASK_PORT=8080 \
    -e API_HOST=backend \ #same as the -h in the docker run above.
    -e API_PORT=7070 \
    --network app-net
    <container image>
```

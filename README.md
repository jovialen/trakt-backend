# Trakt Backend

Backend for Trakt, a cross-platform RSS feed reader.

## Getting started

> [!IMPORTANT]
> This project requires you to use a python version between 3.14 and up to, but not including, 4.0.

[Poetry](https://python-poetry.org/) is used as the package manager for this repo. As such, you need it installed
to run it locally.

You can start the dev server by typing the following commands into a terminal in the root of the repo.

```commandline
poetry install
poetry run fastapi dev ./trakt_backend
```

In order to deploy the backend, you need to be able to host it as a docker container. That can
either be on a homelab, VPS, or managed docker container.

In order for your data to persist, you will also have to be able to set up docker containers.
By default, the application expects the volume to be mounted to /app/data.

```commandline
mkdir data
docker build -t trakt-api .
docker run -d --name trakt-api --env-file .env -p 8000:8000 -v ${pwd}/data:/app/data trakt-api
```

For a full deployment, I recommend setting up Caddy with the built frontend and redirecting all
requests starting with /api to the docker container.

```
                Internet
                    │
               80 / 443
                    │
            Caddy or Nginx
           ┌────────┴────────┐
           │                 │
        /api/*            Everything else
           │                 │
           ▼                 ▼
     FastAPI (:8000)     Static Vue files
                          (dist/)
```

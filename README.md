# Trakt Backend

Backend for Trakt, a cross-platform RSS feed reader.

## Getting started

[Poetry](https://python-poetry.org/) is used as the package manager for this repo. As such, you need it installed
to run it locally.

You can start the dev server by typing the following commands into a terminal in the root of the repo.

```commandline
poetry install
poetry run fastapi dev ./trakt_backend
```

In order to deploy the backend, run the following command

```commandline
poetry run fastapi deploy ./trakt_backend
```

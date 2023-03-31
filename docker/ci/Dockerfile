FROM node:lts-alpine as static
ARG ENVIRONMENT

ENV NODE_ENV=$ENVIRONMENT
ENV NOYARNPOSTINSTALL=1

RUN mkdir /code/
WORKDIR /code/

COPY ./project/static/package.json ./project/static/yarn.lock ./

RUN yarn install --prod --frozen-lockfile

FROM python:3.11-slim

ARG ENVIRONMENT

# system
ENV LC_ALL="C.UTF-8" \
    LANG="C.UTF-8" \

    # python
    PYTHONUNBUFFERED=1 \
    # prevents python creating .pyc files
    PYTHONDONTWRITEBYTECODE=1 \

    # pip
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \

    # poetry
    POETRY_VIRTUALENVS_CREATE=false


RUN apt-get update \
    && apt-get install --no-install-recommends -y \
    git \
    curl \
    build-essential \
    libcurl4-openssl-dev  \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /code/project/static

WORKDIR /code/

COPY poetry.lock pyproject.toml ./

RUN pip install -U pip gunicorn uvicorn poetry \
    && case $ENVIRONMENT in \
        development*) poetry install --no-interaction;; \
        *)    poetry install --no-dev --no-interaction;; \
    esac \
    && pip uninstall -y poetry virtualenv virtualenv-clone \
    && rm -Rf /root/.cache/pip/

COPY ./project .

RUN touch config.env \
 && ln -sf conf/config.env config.env

COPY --from=static /code/node_modules ./static/node_modules

CMD ["gunicorn", \
    "main.asgi:application", \
     "-b", "0.0.0.0:8000", \
     "--worker-connections=1000", \
     "--workers=5", \
     "--threads=3", \
     "-k", "uvicorn_worker.UvicornWorker"]

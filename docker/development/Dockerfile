FROM python:3.8-slim

ENV PYTHONUNBUFFERED="1" \
    LC_ALL="C.UTF-8" \
    LANG="C.UTF-8"

ARG ENVIRONMENT

RUN apt-get update \
    && apt-get install --no-install-recommends -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /code/

WORKDIR /code/

COPY Pipfile* ./

RUN pip install -U pip pipenv gunicorn \
    && case $ENVIRONMENT in \
          dev*) pipenv install --system --dev;; \
          *)    pipenv install --system;; \
        esac \
    && pip uninstall -y pipenv virtualenv virtualenv-clone \
    && rm -Rf /root/.cache/pip/

COPY ./project /code/

COPY docker/development/*.sh /usr/bin/

RUN chmod +x /usr/bin/*.sh

ENTRYPOINT ["/usr/bin/entrypoint.sh"]

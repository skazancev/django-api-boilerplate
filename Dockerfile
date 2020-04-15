FROM python:3.8-slim

ENV PYTHONUNBUFFERED="1" \
    LC_ALL="C.UTF-8" \
    LANG="C.UTF-8"

RUN apt-get update && \
    apt-get install --no-install-recommends -y git && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /code/

WORKDIR /code/

ADD Pipfile* ./

RUN pip install -U pip pipenv gunicorn && \
    pipenv install --system && \
    pip uninstall -y pipenv virtualenv virtualenv-clone && \
    rm -Rf /root/.cache/pip/

ADD ./project /code/

EXPOSE 8000

ADD docker/entrypoint.sh /usr/bin/entrypoint.sh

RUN chmod +x /usr/bin/entrypoint.sh

ENTRYPOINT ["/usr/bin/entrypoint.sh"]

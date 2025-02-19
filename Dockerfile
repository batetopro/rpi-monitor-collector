FROM python:3.11.3-alpine
LABEL maintainer="georgievi.net"

ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /tmp/requirements.txt
COPY ./monitoring /monitoring

WORKDIR /monitoring

EXPOSE 8000

RUN python -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    # fooo 
    # apk add --update --no-cache postgresql-client jpeg-dev && \
    # apk add --update --no-cache --virtual .tmp-build-dev \
    #     build-base postgresql-dev musl-dev zlib zlib-dev && \
    apk add --update --no-cache  pkgconfig gcc musl-dev mariadb-connector-c-dev linux-headers && \
    /py/bin/pip install -r /tmp/requirements.txt && \
    # if [ $DEV = "true" ]; \
    #    then /py/bin/pip install -r /tmp/requirements.dev.txt ; \
    # fi && \
    rm -rf /tmp && \
    # apk del .tmp-build-dev && \
    adduser --disabled-password --no-create-home rpi-manager && \
        mkdir -p /vol/web/history && \
        mkdir -p /vol/locks && \
        mkdir -p /vol/keys && \
        mkdir -p /vol/web/static

RUN chown -R rpi-manager:rpi-manager /vol && \
    chmod -R 0755 /vol

ENV PATH="/py/bin:$PATH"

USER rpi-manager

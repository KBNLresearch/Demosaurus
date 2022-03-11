FROM python:3.7.12-slim as base
MAINTAINER Sara Veldhoen <sara.veldhoen@kb.nl>

RUN pip install --upgrade pip
COPY requirements.txt /
RUN apt-get update && \
    apt-get install -y \
        build-essential \
        make \
        gcc \
    && pip install -r requirements.txt \
    && apt-get remove -y --purge make gcc build-essential \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*
ENV HOME=/usr

RUN groupadd -g 999 user && \
    useradd -r -u 999 -g user user

RUN mkdir /usr/app && chown user:user /usr/app
WORKDIR /usr/app



COPY --chown=user:user demosauruswebapp demosauruswebapp/

USER 999
EXPOSE 3345
ENV GUNICORN_CMD_ARGS="--name demosaurus -w 4 --bind 0.0.0.0:5000 --preload"
CMD ["gunicorn", "demosauruswebapp:create_app()"]

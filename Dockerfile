FROM python:3.9-alpine

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY . /app

RUN pip3 install -U pip && \
    pip3 install -r /app/requirements.txt --no-cache-dir

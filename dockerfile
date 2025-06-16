FROM python:3.11-slim

WORKDIR /freguesia-web

COPY . /freguesia-web

RUN pip install --no-cache-dir -r /freguesia-web/requirements.txt
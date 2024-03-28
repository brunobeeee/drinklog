FROM python:3.12.2-alpine AS builder
WORKDIR /app
COPY app/requirements.txt .
RUN pip3 install -r requirements.txt --no-cache-dir

FROM builder as production
COPY app /app

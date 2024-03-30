FROM python:3.12.2-alpine AS builder

# Set environment variables to prevent caching
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

RUN pip install --upgrade pip
COPY app/requirements.txt .
RUN pip3 install -r requirements.txt --no-cache-dir

FROM builder as production
COPY app /app

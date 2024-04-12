FROM python:3.12.2-alpine AS builder

# Set environment variables to prevent caching
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

RUN apk update && apk add --no-cache nodejs npm make

COPY app/package.json .
COPY app/package-lock.json .
RUN npm install

COPY app/requirements.txt .
RUN pip3 install --upgrade pip && pip3 install -r requirements.txt --no-cache-dir

FROM builder as production
COPY app /app
RUN npm run build

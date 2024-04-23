###############
# DEVELOPMENT #
###############
FROM python:3.12.2-alpine

# Set environment variables to prevent caching
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . .

ENTRYPOINT ["./docker-entrypoint.sh"]

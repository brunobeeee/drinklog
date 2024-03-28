FROM python:3.12.2-alpine AS builder
WORKDIR /app
COPY app/requirements.txt .
RUN pip3 install -r requirements.txt --no-cache-dir

FROM builder as development
ENTRYPOINT ["sleep", "infinity"]

FROM builder as production
COPY app /app
ENTRYPOINT ["python3", "manage.py", "runserver", "0.0.0.0:8000"]

######################
# PRODUCTION-BUILDER #
######################
FROM python:3.12.2-alpine AS builder

# Set environment variables to prevent caching
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install python dependencies
COPY app/requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

WORKDIR /frontend

# Install Node.js
RUN apk update && \
    apk add --no-cache nodejs npm make

# Generate static files
COPY frontend .
RUN npm install --no-update-notifier --no-fund && npm run prod



##############
# PRODUCTION #
##############
FROM python:3.12.2-alpine AS production

# Create the app user
RUN addgroup -S app && adduser -S app -G app

WORKDIR /app

COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache /wheels/*

# Transfer static files from builder stage
COPY --from=builder /frontend/dist /static

# chown all the files to the app user
COPY app .
RUN mkdir -p /var/www/drinklog/static && \
    chown -R app:app /app /static /var/www

USER app

RUN chmod +x docker-entrypoint.prod.sh

ENTRYPOINT ["./docker-entrypoint.prod.sh"]

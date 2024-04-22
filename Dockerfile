###########
# BUILDER #
###########
FROM python:3.12.2-alpine AS builder

# Set environment variables to prevent caching
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

RUN apk update && apk add --no-cache nodejs npm make

COPY /app/package.json .
COPY /app/package-lock.json .
RUN npm install

COPY /app/static/src /app/static/src
COPY /app/generate-favicons.mjs .
RUN npm run prod

# install python dependencies
COPY app/requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt


###############
# DEVELOPMENT #
###############
FROM builder AS development

WORKDIR /app

COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache /wheels/*

COPY app .

ENTRYPOINT ["./docker-entrypoint.sh"]


##############
# PRODUCTION #
##############
FROM python:3.12.2-alpine AS production

# create the app user
RUN addgroup -S app && adduser -S app -G app

# create the appropriate directories
ENV APP_HOME=/app
RUN mkdir $APP_HOME
WORKDIR $APP_HOME

COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache /wheels/*

# copy app & static files
COPY $APP_HOME $APP_HOME
COPY --from=builder /$APP_HOME/static/dist /$APP_HOME/static/dist

# chown all the files to the app user
RUN chown -R app:app $APP_HOME && mkdir /var/www && chown -R app:app /var/www
USER app

RUN chmod +x docker-entrypoint.prod.sh

ENTRYPOINT ["./docker-entrypoint.prod.sh"]

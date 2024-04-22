#!/bin/sh

python manage.py flush --no-input
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser --noinput
python manage.py collectstatic --clear --noinput

apk update && apk add --no-cache nodejs npm make
npm install
mkdir -p /app/static/dist

python manage.py runserver 0.0.0.0:8000 & npm run dev
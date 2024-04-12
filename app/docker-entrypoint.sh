#!/bin/sh

# Wait for Postgres to start
if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."

    while ! nc -z $SQL_HOST $SQL_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

# Then apply migrations
python manage.py flush --no-input
python manage.py migrate
python3 manage.py createsuperuser --noinput

python3 manage.py runserver 0.0.0.0:8000 &
npm run dev

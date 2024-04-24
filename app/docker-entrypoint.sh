#!/bin/sh

if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."

    while ! nc -z $SQL_HOST $SQL_PORT; do
        sleep 0.1
    done

    echo "PostgreSQL started"
fi

# Waiting for the frontend container to produce all /dist files
# This may be the dumbest idea I had in a while, but its for dev env only anyway
sleep 5

python manage.py flush --no-input
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser --noinput
python manage.py collectstatic --link --noinput
python manage.py loaddata initial_data.json

python manage.py runserver 0.0.0.0:8000 
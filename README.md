# drinklog

A habit tracker for tracking water intake.

## Getting started

### Development

To run the app clone this repo and run

```
docker compose up -d
```

This will start the container but not the web app. The `app` folder is mounted to the container so you can read and write from the host machine.
To start the web app run inside the container

```
python3 manage.py runserver 0.0.0.0:8000
```

### Production

To use it in production mode use the `production.yml` file

```
docker compose -f production.yml build
docker compose -f production.yml up -d
```

The web app will be available at `localhost:8000`.

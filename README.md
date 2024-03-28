# drinklog

A habit tracker for tracking water intake.

## Getting started

To run the app clone this repo and run

```
docker compose up -d
```

To use it in production mode use the `production.yml` file

```
docker compose -f production.yml build
docker compose -f production.yml up -d
```

The web app will be available at `localhost:8000`.

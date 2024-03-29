# drinklog

A habit tracker for tracking water intake.

## Getting started

### Development

1. To run the app clone this repo and run

```
docker compose up -d
```

This will start the container but not the web app. The `app` folder is mounted to the container so you can read and write from the host machine.

- (Optional) To start the web app run inside the container

  ```
  docker compose exec web python3 manage.py runserver 0.0.0.0:8000
  ```

- (Optional) To see if the dbs were created correctly run

  ```
  docker compose exec db psql --username=hello_django --dbname=hello_django_dev
  ```

And type `\l` to list all databases.

### Production

To use it in production mode use the `production.yml` file

```
docker compose -f production.yml up -d --build
```

The web app will be available at `localhost:8000`.

> **Hint:** The `--build` flag is required because in production mode the app directory is not mounted to the container.

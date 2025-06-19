# drinklog

A habit tracker for tracking water intake.

## Getting started

### Development

1. To run the app clone this repo and run

   ```
   docker compose up -d
   ```

   This will start the container but not the web app. The `app` folder is mounted to the container so you can read and write from the host machine.
   The web app will be available at `localhost:8000`.

2. (Optional) To start a shell inside the container run

   ```
   docker compose exec web ash
   ```

3. (Optional) To see if the dbs were created correctly run

   ```
   docker compose exec db psql --username=hello_django --dbname=hello_django_dev
   ```

   And type `\l` to list all databases.

### Production

First you have to supply a `.env.prod` and a `.env.prod.db` file to set the env variables. The can look like this:

#### `.env.prod`
```
SECRET_KEY=*****

DJANGO_ALLOWED_HOSTS=localhost 127.0.0.1 [::1]
DJANGO_CSRF_TRUSTED_ORIGINS=https://your.url http://localhost

SQL_ENGINE=django.db.backends.postgresql
SQL_DATABASE=drinklogs
SQL_USER=drinklog
SQL_PASSWORD=*****
SQL_HOST=db
SQL_PORT=5432
DATABASE=postgres

ALLOW_NULL_USERS=False
ALLOW_BLANK_USERS=False
```

#### `.env.prod.db`
```
POSTGRES_DB=drinklogs
POSTGRES_USER=drinklog
POSTGRES_PASSWORD=*****
```

To use it in production mode use the `production.yml` file

```
docker compose -f production.yml up -d --build
```

The web app will be available at `localhost:8000`.

> **Hint:** The `--build` flag is required because in production mode the app directory is not mounted to the container.

#### First run
On the first run in the production environment use these commands to migrate the db an create a admin user:
```
docker compose -f production.yml exec web python manage.py migrate --noinput
docker compose -f production.yml exec web python manage.py createsuperuser
```

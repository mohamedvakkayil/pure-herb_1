# Pure Herb Journal — Django

A Django-based accounting and financial journal application with the Pure Herb template design preserved.

## Setup

1. Activate the virtual environment:
   ```bash
   source venv/bin/activate
   ```

2. Install dependencies (if needed):
   ```bash
   pip install -r requirements.txt
   ```

3. Run migrations (if needed):
   ```bash
   python manage.py migrate
   ```

4. Start the development server:
   ```bash
   python manage.py runserver
   ```

5. Open http://127.0.0.1:8000/ in your browser.

## Deploy to Railway

1. **Push your code** to GitHub (or connect your repo to Railway).

2. **Create a project** at [railway.app](https://railway.app): **New Project** → **Deploy from GitHub repo** → select this repository.

3. **Add PostgreSQL:** In the same project, click **New** → **Database** → **PostgreSQL**. Railway creates a Postgres service and exposes `DATABASE_URL`. In your web service, add a variable: `DATABASE_URL` (use the “Connect” reference from the Postgres service or copy the connection URL).

4. **Configure the web service:** In the web service settings, set:
   - **Build command:** `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate --noinput`
   - **Start command:** leave default (Railway uses the `Procfile`: `gunicorn config.wsgi --bind 0.0.0.0:$PORT`), or set it explicitly to the same.
   - **Environment variables:** `DATABASE_URL` (from Postgres), `SECRET_KEY` (generate a strong random value). Optionally `DEBUG=False`. Railway sets `PORT` and `RAILWAY_PUBLIC_DOMAIN` automatically.

5. **Create a superuser:** After the first deploy, run locally with Railway’s Postgres URL (Dashboard → Postgres → Connect → copy the URL or variable):
   ```bash
   export DATABASE_URL='postgresql://...'   # paste Railway Postgres URL
   python manage.py createsuperuser
   ```
   To reset a password: `python manage.py changepassword mohamed` (with the same `DATABASE_URL` set).

## Features

- **Journal entries** — Create, read, update, delete accounting/financial entries
- **Double-entry bookkeeping** — Each entry has debit/credit lines; totals must balance
- **Django Admin** — Manage entries at http://127.0.0.1:8000/admin/ (create a superuser with `python manage.py createsuperuser`)

## Project Structure

- `config/` — Django project settings
- `journal/` — Journal app (models, views, forms)
- `templates/` — Base and journal templates
- `static/` — CSS and images (logo, styles)

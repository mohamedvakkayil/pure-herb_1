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

## Deploy to Google App Engine

1. **Cloud SQL (PostgreSQL)**  
   Create a Cloud SQL instance, database, and user. Note the instance connection name (`PROJECT_ID:REGION:INSTANCE_NAME`). Set in `app.yaml` (or in App Engine environment variables):
   - `INSTANCE_CONNECTION_NAME`
   - `DJANGO_DB_NAME`, `DJANGO_DB_USER`, `DJANGO_DB_PASSWORD`

2. **Environment variables**  
   Set in Google Cloud Console (App Engine > Settings > Environment variables) or via `gcloud app deploy --set-env-vars`:
   - `SECRET_KEY` — use a strong random value; do not commit it.
   - `ALLOWED_HOSTS` — your App Engine host (e.g. `your-app.uc.r.appspot.com`).
   - Optionally `CSRF_TRUSTED_ORIGINS` — e.g. `https://your-app.uc.r.appspot.com`.

3. **Static files**  
   Run before deploying so `staticfiles/` is present and uploaded:
   ```bash
   python manage.py collectstatic --noinput
   ```

4. **Deploy**  
   From the project root:
   ```bash
   gcloud app deploy
   ```
   After the first deploy, update `app.yaml` or env vars with the actual app URL if you used a placeholder.

## Deploy to Render

1. **Push your code** to GitHub, GitLab, or Bitbucket.

2. **Create a Blueprint**  
   - Go to [dashboard.render.com](https://dashboard.render.com) → **New** → **Blueprint**.  
   - Connect the repo that contains `render.yaml`.  
   - Render will create a web service and a PostgreSQL database and wire `DATABASE_URL` and `SECRET_KEY` automatically.

3. **Deploy**  
   - Click **Apply**; Render runs `build.sh` (install deps, collectstatic, migrate) then starts the app with Gunicorn.  
   - Your app will be at `https://pure-herb-journal.onrender.com` (or the name you give the service).

4. **Optional – manual setup**  
   - Instead of a Blueprint, create a **Web Service** and a **PostgreSQL** database manually.  
   - Set **Build Command:** `./build.sh`  
   - Set **Start Command:** `gunicorn config.wsgi --bind 0.0.0.0:$PORT`  
   - Add env vars: `DATABASE_URL` (from the database), `SECRET_KEY` (generate in dashboard).  
   - `ALLOWED_HOSTS` and `CSRF_TRUSTED_ORIGINS` are set automatically from `RENDER_EXTERNAL_HOSTNAME`.

5. **Create a superuser** (after first deploy)  
   - In the Render dashboard, open your web service → **Shell** → run:  
     `python manage.py createsuperuser`

## Features

- **Journal entries** — Create, read, update, delete accounting/financial entries
- **Double-entry bookkeeping** — Each entry has debit/credit lines; totals must balance
- **Django Admin** — Manage entries at http://127.0.0.1:8000/admin/ (create a superuser with `python manage.py createsuperuser`)

## Project Structure

- `config/` — Django project settings
- `journal/` — Journal app (models, views, forms)
- `templates/` — Base and journal templates
- `static/` — CSS and images (logo, styles)

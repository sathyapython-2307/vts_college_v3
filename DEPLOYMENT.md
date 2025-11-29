# Render deployment checklist for this Django app

Prerequisites
- A Render account and a GitHub repo connected to Render.
- A managed Postgres database (recommended) or use Render's managed DB.

Required Render environment variables (exact keys)
- `SECRET_KEY` : Your Django secret for production (generate a strong value).
- `DEBUG` : `False` in production.
- `ALLOWED_HOSTS` : comma-separated hostnames (e.g. `your-app.onrender.com,example.com`).
- `DATABASE_URL` : connection string for Postgres (e.g. `postgres://...`).
- `RAZORPAY_KEY_ID` and `RAZORPAY_KEY_SECRET` (if payments enabled).

Build & Start commands (Render service config)
- Build command: `pip install -r requirements-pinned.txt && python manage.py migrate --noinput && python manage.py collectstatic --noinput`
- Start command: `gunicorn Online_Course.wsgi:application --bind 0.0.0.0:$PORT`

What the repo changes include
- `requirements-pinned.txt` : pinned packages for predictable deploys.
- `Procfile` : starts Gunicorn worker.
- `render.yaml` : sample Render service config (runs migrate + collectstatic).
- `runtime.txt` : sets Python runtime.
- A `/healthz/` endpoint and a `scripts/post_deploy_check.py` script to verify deploy success.
- Template fixes to use `{% static '...' %}` where needed so WhiteNoise serves assets.

Database setup steps
1. Create a managed Postgres database on Render (or external Postgres).
2. Set `DATABASE_URL` in Render environment settings using the DB connection string.
3. Render buildCommand will run `python manage.py migrate --noinput` to create missing tables.

Collectstatic and media
- `python manage.py collectstatic --noinput` runs during build to populate `staticfiles` (STATIC_ROOT).
- Static files served by WhiteNoise from the app. For large or mutable media (user uploads) prefer S3 or another cloud storage; set `MEDIA_URL` and `MEDIA_ROOT` accordingly and update `DEFAULT_FILE_STORAGE` if using S3.

HTTPS & security
- Set `DEBUG` to `False` in Render env.
- Ensure `SECRET_KEY` is set and private.
- When `DEBUG=False` the following are enforced in `Online_Course/settings.py`: HSTS, `SECURE_SSL_REDIRECT`, secure cookies, and `SECURE_PROXY_SSL_HEADER` for Render.

Rollback steps (quick)
1. On Render, in the service > Deploys view, click the previous deploy and select "Promote" or "Rollback" (Render UI provides this).
2. If a DB migration introduced breaking schema changes, restore DB from a backup or revert schema manually. Always backup DB before production migrations.

Post-deploy verification
1. Use Render's health check (`/healthz/`) or run locally:
   ```powershell
   $env:TARGET_URL='https://your-app.onrender.com'
   python .\scripts\post_deploy_check.py
   ```
2. Confirm homepage returns 200 and that at least common static files return 200 (warnings printed if missing).

Notes and recommendations
- Consider using a managed object storage (S3 / DigitalOcean Spaces / Render Storage) for `MEDIA_ROOT` and set `DEFAULT_FILE_STORAGE` to `storages.backends.s3boto3.S3Boto3Storage` for production.
- Keep `requirements-pinned.txt` updated by running `pip-compile` or using `pip freeze` from a known environment and committing the file.
- If you want zero-downtime migrations consider using Django's migration best practices (create nullable fields, backfill, then make non-nullable in a later deploy).

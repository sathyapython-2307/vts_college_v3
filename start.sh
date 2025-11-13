#!/usr/bin/env bash
set -euo pipefail

# Run migrations and collectstatic, then exec gunicorn. Using exec so signals
# are forwarded correctly.
python manage.py migrate --no-input
python manage.py collectstatic --no-input

# Exec gunicorn so it becomes PID 1 in the container/process and receives signals
exec gunicorn --bind 0.0.0.0:$PORT Online_Course.wsgi:application --timeout 120 --workers 4 --access-logfile - --error-logfile -

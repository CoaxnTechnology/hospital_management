#!/bin/bash
set -e

# Live paths on this VPS. The Postgres DB, /var/www/data, .env, venv and logs
# are NEVER touched by this script: migrate only applies schema changes
# (no data deletion), and no loaddata/flush/clear command is run here.
APP_DIR="/var/www/echo"
VENV_DIR="/var/www/echo/venv"

cd "$APP_DIR"

# Fail fast with a clear message if secrets are missing, instead of Django
# silently falling back to default DB credentials (which causes 500s).
if [ ! -f "$APP_DIR/.env" ]; then
    echo "ERROR: $APP_DIR/.env not found, refusing to start (would use wrong DB credentials)."
    exit 1
fi

# Ensure required directories exist
mkdir -p logs
chmod +x "$APP_DIR/deploy/run.sh"

export DJANGO_SETTINGS_MODULE="echo.settings.production"

# Install dependencies (skip backports.zoneinfo — built into Python 3.9+)
"$VENV_DIR/bin/python" -m pip install -r requirements.txt --quiet

# Collect static files (ignore duplicate file warnings)
"$VENV_DIR/bin/python" manage.py collectstatic --noinput 2>&1

# Run database migrations (schema only — never deletes data; no flush/loaddata here)
"$VENV_DIR/bin/python" manage.py migrate --noinput

# Refresh supervisor configs (Ubuntu layout) and restart app services only.
# Targeted restarts: other supervised processes and the DB are left alone.
cp "$APP_DIR/deploy/supervisor-gunicorn.conf" /etc/supervisor/conf.d/echo-gunicorn.conf
cp "$APP_DIR/deploy/supervisor-daphne.conf" /etc/supervisor/conf.d/echo-daphne.conf
cp "$APP_DIR/deploy/supervisor-store.conf" /etc/supervisor/conf.d/echo-store.conf
supervisorctl reread
supervisorctl update
supervisorctl restart echo-gunicorn echo-daphne

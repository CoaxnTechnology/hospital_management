#!/bin/bash
set -e

APP_DIR="/home/echo/app/echo"
VENV_DIR="/home/echo/venv"

cd "$APP_DIR"

# Ensure required directories exist and correct ownership
mkdir -p logs data
chown -R echo:echo /home/echo/app

# Load environment variables
set -a
source /home/echo/app/.env
set +a

# Activate virtual environment
source "$VENV_DIR/bin/activate"

# Install dependencies (skip backports.zoneinfo — built into Python 3.9+)
pip install -r requirements.txt --quiet

# Collect static files (ignore duplicate file warnings)
python manage.py collectstatic --noinput 2>&1

# Run database migrations
python manage.py migrate --noinput

# Update supervisor configs and restart services
cp "$APP_DIR/deploy/supervisor-gunicorn.conf" /etc/supervisord.d/echo-gunicorn.ini
cp "$APP_DIR/deploy/supervisor-daphne.conf" /etc/supervisord.d/echo-daphne.ini
cp "$APP_DIR/deploy/supervisor-worklist.conf" /etc/supervisord.d/echo-worklist.ini
cp "$APP_DIR/deploy/supervisor-store.conf" /etc/supervisord.d/echo-store.ini
supervisorctl reread
supervisorctl update
supervisorctl restart all

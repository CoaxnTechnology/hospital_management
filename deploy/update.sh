#!/usr/bin/env bash
set -euo pipefail

APP_DIR="/home/echo/app"
VENV_DIR="/home/echo/venv"

cd "$APP_DIR"

# Load environment variables
set -a
source .env
set +a

# Activate virtual environment
source "$VENV_DIR/bin/activate"

# Install dependencies (skip backports.zoneinfo — built into Python 3.9+)
pip install -r requirements.txt --quiet

# Collect static files
python manage.py collectstatic --noinput

# Run database migrations
python manage.py migrate --noinput

# Restart all supervisor-managed services
supervisorctl restart all

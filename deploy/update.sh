#!/bin/bash
set -e

APP_DIR="/home/echo/app/echo"
VENV_DIR="/home/echo/venv"

cd "$APP_DIR"

# Ensure required directories exist
mkdir -p logs data

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

# Restart all supervisor-managed services
supervisorctl restart all

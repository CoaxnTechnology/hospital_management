#!/usr/bin/env bash
set -euo pipefail

# ============================================================
# provision_hostinger.sh
# Automated provisioning for echo (Django) on Hostinger VPS
# Tested on Ubuntu 20.04 / 22.04
# ============================================================

RED='\033[0;31m'; GREEN='\033[0;32m'; CYAN='\033[0;36m'; NC='\033[0m'
info()  { echo -e "${CYAN}[INFO]${NC}  $*"; }
ok()    { echo -e "${GREEN}[OK]${NC}    $*"; }
fail()  { echo -e "${RED}[FAIL]${NC}  $*"; exit 1; }

# ---- Configuration prompts ----
read -rp "Enter your domain (e.g., echo.example.com): " DOMAIN
[[ -z "$DOMAIN" ]] && fail "Domain is required."

read -rsp "Enter PostgreSQL password for user 'django': " DB_PASS
echo
[[ -z "$DB_PASS" ]] && fail "Database password is required."

read -rp "Enter your email for Let's Encrypt SSL: " SSL_EMAIL
[[ -z "$SSL_EMAIL" ]] && SSL_EMAIL="admin@${DOMAIN}"

SECRET_KEY=$(python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())" 2>/dev/null || uuidgen)

REPO_URL="git@github.com:CoaxnTechnology/hospital_management.git"
APP_DIR="/home/echo"
VENV_DIR="${APP_DIR}/venv"
PROJECT_DIR="${APP_DIR}/echo"
DATA_DIR="${APP_DIR}/data"
LOG_DIR="${PROJECT_DIR}/logs"
DEPLOY_LOG_DIR="${APP_DIR}/deploy/logs"

# ============================================================
info "Starting provisioning on $(hostname) for domain ${DOMAIN}..."
# ============================================================

# ---- System update ----
info "Updating system packages..."
apt-get update -y && apt-get upgrade -y

# ---- Dependencies ----
info "Installing system dependencies..."
apt-get install -y \
    python3 python3-venv python3-dev python3-pip \
    libpq-dev build-essential \
    postgresql postgresql-contrib \
    redis-server \
    nginx \
    supervisor \
    memcached \
    certbot python3-certbot-nginx \
    git curl wget ufw

ok "System dependencies installed."

# ---- PostgreSQL ----
info "Configuring PostgreSQL..."
systemctl start postgresql
systemctl enable postgresql

sudo -u postgres psql <<SQL
CREATE USER django WITH PASSWORD '${DB_PASS}';
ALTER ROLE django SET client_encoding TO 'utf8';
ALTER ROLE django SET default_transaction_isolation TO 'read committed';
ALTER ROLE django SET timezone TO 'UTC';
CREATE DATABASE echoapp WITH ENCODING 'UTF8' TEMPLATE template0 OWNER django;
GRANT ALL PRIVILEGES ON DATABASE echoapp TO django;
SQL
ok "PostgreSQL configured (database: echoapp, user: django)."

# ---- Clone repository ----
info "Cloning repository..."
mkdir -p "${APP_DIR}"
git clone "${REPO_URL}" "${APP_DIR}"
ok "Repository cloned to ${APP_DIR}."

# ---- Python virtual environment ----
info "Setting up Python virtual environment..."
python3 -m venv "${VENV_DIR}"
source "${VENV_DIR}/bin/activate"
pip install --upgrade pip setuptools wheel
pip install -r "${PROJECT_DIR}/requirements.txt"
pip install pylibjpeg pylibjpeg-libjpeg opencv-python-headless pynetdicom "numpy<2" "pydicom>=2.3"
ok "Python dependencies installed."

# ---- Create .env ----
info "Creating .env file..."
cat > "${PROJECT_DIR}/.env" <<EOF
DEBUG=False
DB_NAME=echoapp
DB_USER=django
DB_PASS=${DB_PASS}
DB_HOST=127.0.0.1
DB_PORT=5432
SECRET_KEY=${SECRET_KEY}
SUBDOMAIN=${DOMAIN}
REDIS_HOST=127.0.0.1
REDIS_PORT=6379
CERTBOT_EMAIL=${SSL_EMAIL}
EOF
ok ".env created."

# ---- Create directories ----
info "Creating data and log directories..."
mkdir -p "${DATA_DIR}"
mkdir -p "${LOG_DIR}"
mkdir -p "${DEPLOY_LOG_DIR}"
chmod -R 755 "${DATA_DIR}"
ok "Directories created."

# ---- Django setup ----
info "Running Django migrations..."
cd "${PROJECT_DIR}"
export DJANGO_SETTINGS_MODULE="echo.settings.production"
python manage.py migrate --noinput
ok "Migrations complete."

info "Collecting static files..."
python manage.py collectstatic --noinput --clear
ok "Static files collected."

info "Creating superuser (you will be prompted)..."
python manage.py createsuperuser || true

# ---- Nginx configuration ----
info "Configuring Nginx..."
cat > /etc/nginx/sites-available/echo <<NGINX
server {
    listen 80;
    server_name ${DOMAIN};
    client_max_body_size 100M;

    location /static/ {
        alias ${PROJECT_DIR}/public/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /data/ {
        alias ${DATA_DIR}/;
        expires 7d;
    }

    location /ws/ {
        proxy_pass http://127.0.0.1:9000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_read_timeout 86400s;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_read_timeout 300s;
    }
}
NGINX

ln -sf /etc/nginx/sites-available/echo /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl reload nginx
ok "Nginx configured."

# ---- SSL (Let's Encrypt) ----
info "Obtaining SSL certificate from Let's Encrypt..."
certbot --nginx -d "${DOMAIN}" --non-interactive --agree-tos --email "${SSL_EMAIL}" || {
    echo -e "${RED}[WARN]${NC} Certbot failed. You can run it later manually: certbot --nginx -d ${DOMAIN}"
}
ok "SSL configured."

# ---- Supervisor ----
info "Configuring Supervisor..."

cat > /etc/supervisor/conf.d/echo-gunicorn.conf <<SUPER
[program:echo-gunicorn]
command=${VENV_DIR}/bin/gunicorn echo.wsgi:application --bind 127.0.0.1:8000 --workers 3 --timeout 120
directory=${PROJECT_DIR}
user=root
autostart=true
autorestart=true
stderr_logfile=${DEPLOY_LOG_DIR}/gunicorn.err.log
stdout_logfile=${DEPLOY_LOG_DIR}/gunicorn.out.log
environment=DJANGO_SETTINGS_MODULE="echo.settings.production"
SUPER

cat > /etc/supervisor/conf.d/echo-daphne.conf <<SUPER
[program:echo-daphne]
command=${VENV_DIR}/bin/daphne -b 127.0.0.1 -p 9000 echo.asgi:application
directory=${PROJECT_DIR}
user=root
autostart=true
autorestart=true
stderr_logfile=${DEPLOY_LOG_DIR}/daphne.err.log
stdout_logfile=${DEPLOY_LOG_DIR}/daphne.out.log
environment=DJANGO_SETTINGS_MODULE="echo.settings.production"
SUPER

cat > /etc/supervisor/conf.d/echo-store.conf <<SUPER
[program:echo-store]
command=${VENV_DIR}/bin/python ${PROJECT_DIR}/store.py
directory=${PROJECT_DIR}
user=root
autostart=true
autorestart=true
stderr_logfile=${DEPLOY_LOG_DIR}/store.err.log
stdout_logfile=${DEPLOY_LOG_DIR}/store.out.log
SUPER

supervisorctl reread
supervisorctl update
supervisorctl start all
ok "Supervisor processes started."

# ---- Firewall ----
info "Configuring UFW firewall..."
ufw --force reset
ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable
ok "Firewall enabled (SSH, HTTP, HTTPS)."

# ---- Health check ----
info "Running health checks..."
sleep 3
supervisorctl status

echo ""
if curl -sI "http://127.0.0.1:8000" | grep -q "200\|302"; then
    ok "Gunicorn responds on port 8000."
else
    fail "Gunicorn health check failed. Check logs: ${DEPLOY_LOG_DIR}/gunicorn.err.log"
fi

if curl -sI "https://${DOMAIN}" | grep -q "200\|301\|302"; then
    ok "Site is reachable via HTTPS."
else
    echo -e "${RED}[WARN]${NC} HTTPS check failed. DNS may not be propagated yet."
fi

# ============================================================
echo ""
echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}  Provisioning complete!${NC}"
echo -e "${GREEN}  Domain: https://${DOMAIN}${NC}"
echo -e "${GREEN}  Admin:  https://${DOMAIN}/admin/${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""
echo "Next steps if DNS is not yet pointed:"
echo "  1. Point your domain's DNS A record to this server's IP."
echo "  2. Wait for propagation, then run: certbot --nginx -d ${DOMAIN}"
echo "  3. Verify HTTPS is working."
echo ""
echo "PostgreSQL credentials (printed once — save them):"
echo "  Database: echoapp"
echo "  User:     django"
echo "  Password: ${DB_PASS}"
echo ""
echo "Logs: ${DEPLOY_LOG_DIR}/"

#!/bin/bash
# =====================================================================
# Echo App — Bluehost VPS Deployment Script (CentOS / AlmaLinux)
# =====================================================================
#
# BEFORE RUNNING:
# 1. Edit /home/echo/echo/.env with your actual values
# 2. Create a DNS A record for the subdomain pointing to your VPS IP
# 3. Upload this project to the VPS (rsync or scp — see step 5)
#
# USAGE:
#   ssh root@YOUR_VPS_IP
#   chmod +x /home/echo/echo/deploy/deploy.sh
#   /home/echo/echo/deploy/deploy.sh
#
# =====================================================================

set -euo pipefail

APP_USER="echo"
APP_HOME="/home/${APP_USER}"
APP_DIR="${APP_HOME}/echo"
VENV_DIR="${APP_HOME}/venv"
DATA_DIR="${APP_HOME}/data"
ENV_FILE="${APP_DIR}/.env"

# ------------------------------------------------------------------
# Load .env
# ------------------------------------------------------------------
if [ -f "${ENV_FILE}" ]; then
    echo "Loading configuration from ${ENV_FILE}..."
    set -a
    source <(grep -v '^\s*#' "${ENV_FILE}" | grep -v '^\s*$')
    set +a
else
    echo "ERROR: ${ENV_FILE} not found."
    echo "Copy .env.example to .env and fill in your values first."
    exit 1
fi

# Validate required vars
for var in SUBDOMAIN VPS_IP SECRET_KEY DB_NAME DB_USER DB_PASS CERTBOT_EMAIL; do
    if [ -z "${!var:-}" ]; then
        echo "ERROR: ${var} is not set in ${ENV_FILE}"
        exit 1
    fi
done

echo "============================================="
echo " Echo App Deployment — ${SUBDOMAIN}"
echo "============================================="

# ------------------------------------------------------------------
# 1. System packages
# ------------------------------------------------------------------
echo "[1/10] Installing system packages..."
dnf -y update
dnf -y install epel-release
dnf -y install \
    nginx \
    postgresql-server postgresql-devel postgresql-contrib \
    redis memcached \
    supervisor \
    gcc gcc-c++ make \
    python3 python3-devel python3-pip \
    openssl-devel libffi-devel zlib-devel bzip2-devel \
    certbot python3-certbot-nginx \
    firewalld

# ------------------------------------------------------------------
# 2. Create app user & directory structure
# ------------------------------------------------------------------
echo "[2/10] Creating app user and directories..."
if ! id "${APP_USER}" &>/dev/null; then
    useradd -m -s /bin/bash "${APP_USER}"
fi
mkdir -p "${APP_DIR}" "${DATA_DIR}" "${VENV_DIR}"
mkdir -p "${APP_DIR}/logs"
mkdir -p /var/log/supervisor

# ------------------------------------------------------------------
# 3. PostgreSQL setup
# ------------------------------------------------------------------
echo "[3/10] Setting up PostgreSQL..."
if [ ! -f /var/lib/pgsql/data/pg_hba.conf ]; then
    postgresql-setup --initdb
fi
systemctl enable postgresql
systemctl start postgresql

sudo -u postgres psql -c "CREATE USER ${DB_USER} WITH PASSWORD '${DB_PASS}';" 2>/dev/null || true
sudo -u postgres psql -c "ALTER ROLE ${DB_USER} SET client_encoding TO 'utf8';" 2>/dev/null || true
sudo -u postgres psql -c "ALTER ROLE ${DB_USER} SET default_transaction_isolation TO 'read committed';" 2>/dev/null || true
sudo -u postgres psql -c "ALTER ROLE ${DB_USER} SET timezone TO 'UTC';" 2>/dev/null || true
sudo -u postgres psql -c "CREATE DATABASE ${DB_NAME} WITH ENCODING 'UTF8' TEMPLATE template0;" 2>/dev/null || true
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE ${DB_NAME} TO ${DB_USER};" 2>/dev/null || true

# Allow local password authentication
if ! grep -q "host.*${DB_NAME}.*${DB_USER}" /var/lib/pgsql/data/pg_hba.conf; then
    sed -i '/^# IPv4 local connections/a host    '"${DB_NAME}"'    '"${DB_USER}"'    127.0.0.1/32    md5' /var/lib/pgsql/data/pg_hba.conf
    systemctl restart postgresql
fi

# To import a dump: sudo -u postgres psql ${DB_NAME} < /path/to/dump.sql
if [ -f "${APP_DIR}/echoapp_db_export.sql" ]; then
    echo "Importing database dump..."
    sudo -u postgres psql -d "${DB_NAME}" < "${APP_DIR}/echoapp_db_export.sql" || true
fi

# ------------------------------------------------------------------
# 4. Redis & Memcached
# ------------------------------------------------------------------
echo "[4/10] Starting Redis and Memcached..."
systemctl enable redis memcached
systemctl start redis memcached

# ------------------------------------------------------------------
# 5. Upload project files
# ------------------------------------------------------------------
echo "[5/10] Project files..."
echo "  -> Make sure project files are already in ${APP_DIR}"
echo "  -> From your LOCAL machine, run:"
echo "     rsync -avz --exclude='venv' --exclude='__pycache__' --exclude='.git' \\"
echo "       /home/raza/Projects/test/echo/ root@${VPS_IP}:${APP_DIR}/"

if [ ! -f "${APP_DIR}/manage.py" ]; then
    echo "WARNING: manage.py not found in ${APP_DIR}. Upload project files first."
    echo "Continuing anyway — you can re-run this script after uploading."
fi

# ------------------------------------------------------------------
# 6. Python virtualenv & dependencies
# ------------------------------------------------------------------
echo "[6/10] Setting up Python virtual environment..."
python3 -m venv "${VENV_DIR}"
source "${VENV_DIR}/bin/activate"

pip install --upgrade pip setuptools wheel

if [ -f "${APP_DIR}/requirements.txt" ]; then
    grep -v 'backports.zoneinfo' "${APP_DIR}/requirements.txt" | pip install -r /dev/stdin
fi

pip install pylibjpeg pylibjpeg-libjpeg opencv-python-headless pynetdicom 'numpy<2' 'pydicom>=2.3'

deactivate

# ------------------------------------------------------------------
# 7. Django setup
# ------------------------------------------------------------------
echo "[7/10] Running Django setup..."
if [ -f "${APP_DIR}/manage.py" ]; then
    cd "${APP_DIR}"
    "${VENV_DIR}/bin/python" manage.py collectstatic --noinput
    "${VENV_DIR}/bin/python" manage.py migrate --fake-initial

    # Create superuser if not exists
    if [ -n "${ADMIN_USER:-}" ] && [ -n "${ADMIN_PASS:-}" ]; then
        echo "Creating admin superuser..."
        "${VENV_DIR}/bin/python" manage.py shell << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='${ADMIN_USER}').exists():
    User.objects.create_superuser('${ADMIN_USER}', '${ADMIN_EMAIL:-admin@localhost}', '${ADMIN_PASS}')
    print('Superuser created')
else:
    print('Superuser already exists')
EOF
    fi
fi

# ------------------------------------------------------------------
# 8. Fix ownership
# ------------------------------------------------------------------
echo "[8/10] Fixing file ownership..."
chown -R "${APP_USER}:${APP_USER}" "${APP_HOME}"

# ------------------------------------------------------------------
# 9. Supervisor configs
# ------------------------------------------------------------------
echo "[9/10] Setting up Supervisor..."
cp "${APP_DIR}/deploy/supervisor-gunicorn.conf" /etc/supervisord.d/echo-gunicorn.ini
cp "${APP_DIR}/deploy/supervisor-daphne.conf"   /etc/supervisord.d/echo-daphne.ini
cp "${APP_DIR}/deploy/supervisor-worklist.conf"  /etc/supervisord.d/echo-worklist.ini
cp "${APP_DIR}/deploy/supervisor-store.conf"     /etc/supervisord.d/echo-store.ini

systemctl enable supervisord
systemctl restart supervisord
supervisorctl reread
supervisorctl update

# ------------------------------------------------------------------
# 10. Nginx + SSL
# ------------------------------------------------------------------
echo "[10/10] Setting up Nginx and SSL..."

# Prepare Nginx config from template — replace placeholders
cp "${APP_DIR}/deploy/nginx-site.conf" /etc/nginx/conf.d/echo.conf
sed -i "s/YOUR_SUBDOMAIN/${SUBDOMAIN}/g" /etc/nginx/conf.d/echo.conf

rm -f /etc/nginx/conf.d/default.conf

# Temporarily use HTTP-only config for certbot to get the cert
cat > /etc/nginx/conf.d/echo-temp.conf <<TEMPNGINX
server {
    listen 80;
    server_name ${SUBDOMAIN};
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
TEMPNGINX

mv /etc/nginx/conf.d/echo.conf /etc/nginx/conf.d/echo.conf.disabled

systemctl enable nginx
nginx -t && systemctl restart nginx

echo "Obtaining SSL certificate for ${SUBDOMAIN}..."
certbot --nginx -d "${SUBDOMAIN}" --non-interactive --agree-tos --email "${CERTBOT_EMAIL}" --redirect || {
    echo "WARNING: Certbot failed. You can run it manually later:"
    echo "  certbot --nginx -d ${SUBDOMAIN}"
}

rm -f /etc/nginx/conf.d/echo-temp.conf
mv /etc/nginx/conf.d/echo.conf.disabled /etc/nginx/conf.d/echo.conf

nginx -t && systemctl restart nginx

# Auto-renewal cron
(crontab -l 2>/dev/null; echo "0 3 * * * certbot renew --quiet --post-hook 'systemctl reload nginx'") | sort -u | crontab -

# ------------------------------------------------------------------
# Firewall
# ------------------------------------------------------------------
echo "Configuring firewall..."
systemctl enable firewalld
systemctl start firewalld
firewall-cmd --permanent --add-service=ssh
firewall-cmd --permanent --add-service=http
firewall-cmd --permanent --add-service=https
firewall-cmd --permanent --add-port=${DICOM_WORKLIST_PORT:-11112}/tcp
firewall-cmd --permanent --add-port=${DICOM_STORE_PORT:-11113}/tcp
firewall-cmd --reload

# ------------------------------------------------------------------
# Done
# ------------------------------------------------------------------
echo ""
echo "============================================="
echo " Deployment complete!"
echo "============================================="
echo ""
supervisorctl status
echo ""
echo "Verify:"
echo "  Web:   https://${SUBDOMAIN}"
echo "  DICOM: python -m pynetdicom echoscu ${VPS_IP} ${DICOM_WORKLIST_PORT:-11112}"
echo ""

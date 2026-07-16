#!/bin/bash
set -euo pipefail

APP_DIR="/var/www/echo"
VENV_DIR="/var/www/echo/venv"
DATA_DIR="/var/www/data"
ENV_FILE="${APP_DIR}/.env"

if [ -f "${ENV_FILE}" ]; then
    echo "Loading configuration from ${ENV_FILE}..."
    set -a
    source <(grep -v '^\s*#' "${ENV_FILE}" | grep -v '^\s*$')
    set +a
else
    echo "ERROR: ${ENV_FILE} not found."
    exit 1
fi

for var in SUBDOMAIN VPS_IP SECRET_KEY DB_NAME DB_USER DB_PASS CERTBOT_EMAIL; do
    if [ -z "${!var:-}" ]; then
        echo "ERROR: ${var} is not set in ${ENV_FILE}"
        exit 1
    fi
done

echo "============================================="
echo " Echo App Deployment — ${SUBDOMAIN}"
echo "============================================="

echo "[1/10] Installing system packages..."
dnf -y update
dnf -y install epel-release
dnf -y install nginx postgresql-server postgresql-devel postgresql-contrib redis memcached supervisor gcc gcc-c++ make python3 python3-devel python3-pip openssl-devel libffi-devel zlib-devel bzip2-devel certbot python3-certbot-nginx firewalld

echo "[2/10] Creating directories..."
mkdir -p "${APP_DIR}" "${DATA_DIR}" "${VENV_DIR}"
mkdir -p "${APP_DIR}/logs" "${APP_DIR}/storage" "${APP_DIR}/uploads"

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

if ! grep -q "host.*${DB_NAME}.*${DB_USER}" /var/lib/pgsql/data/pg_hba.conf; then
    sed -i '/^# IPv4 local connections/a host    '"${DB_NAME}"'    '"${DB_USER}"'    127.0.0.1/32    md5' /var/lib/pgsql/data/pg_hba.conf
    systemctl restart postgresql
fi

if [ -f "${APP_DIR}/echoapp_db_export.sql" ]; then
    echo "Importing database dump..."
    sudo -u postgres psql -d "${DB_NAME}" < "${APP_DIR}/echoapp_db_export.sql" || true
fi

echo "[4/10] Starting Redis and Memcached..."
systemctl enable redis memcached
systemctl start redis memcached

echo "[5/10] Project files..."
if [ ! -f "${APP_DIR}/manage.py" ]; then
    echo "WARNING: manage.py not found. Upload project files first."
fi

echo "[6/10] Setting up Python virtual environment..."
python3 -m venv "${VENV_DIR}"
source "${VENV_DIR}/bin/activate"
pip install --upgrade pip setuptools wheel
grep -v 'backports.zoneinfo' "${APP_DIR}/requirements.txt" | pip install -r /dev/stdin
pip install pylibjpeg pylibjpeg-libjpeg opencv-python-headless pynetdicom 'numpy<2' 'pydicom>=2.3'
deactivate

echo "[7/10] Running Django setup..."
cd "${APP_DIR}"
"${VENV_DIR}/bin/python" manage.py collectstatic --noinput --settings=echo.settings.production
"${VENV_DIR}/bin/python" manage.py migrate --settings=echo.settings.production

echo "[8/10] Setting permissions..."
groupadd -f echoapp
chown -R root:echoapp "${APP_DIR}" "${DATA_DIR}"
find "${APP_DIR}" -type d -exec chmod 750 {} \;
find "${APP_DIR}" -type f -exec chmod 640 {} \;
chmod 750 "${APP_DIR}/manage.py" "${APP_DIR}/store.py"
chmod 644 "${APP_DIR}/static/" -R 2>/dev/null || true
chmod 755 "${APP_DIR}/static/" -R 2>/dev/null || true
chown malekhentati:echoapp "${APP_DIR}/logs" "${APP_DIR}/storage" "${APP_DIR}/uploads"
chmod 770 "${APP_DIR}/logs" "${APP_DIR}/storage" "${APP_DIR}/uploads"
usermod -aG echoapp malekhentati
usermod -aG echoapp www-data

echo "[9/10] Setting up Supervisor..."
cp "${APP_DIR}/deploy/supervisor-gunicorn.conf" /etc/supervisord.d/echo-gunicorn.ini
cp "${APP_DIR}/deploy/supervisor-daphne.conf" /etc/supervisord.d/echo-daphne.ini
systemctl enable supervisord
systemctl restart supervisord
supervisorctl reread
supervisorctl update

echo "[10/10] Setting up Nginx and SSL..."
cp "${APP_DIR}/deploy/nginx-site.conf" /etc/nginx/conf.d/echo.conf
sed -i "s/YOUR_SUBDOMAIN/${SUBDOMAIN}/g" /etc/nginx/conf.d/echo.conf
rm -f /etc/nginx/conf.d/default.conf

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

certbot --nginx -d "${SUBDOMAIN}" --non-interactive --agree-tos --email "${CERTBOT_EMAIL}" --redirect || {
    echo "WARNING: Certbot failed. Run manually: certbot --nginx -d ${SUBDOMAIN}"
}

rm -f /etc/nginx/conf.d/echo-temp.conf
mv /etc/nginx/conf.d/echo.conf.disabled /etc/nginx/conf.d/echo.conf
nginx -t && systemctl restart nginx

(crontab -l 2>/dev/null; echo "0 3 * * * certbot renew --quiet --post-hook 'systemctl reload nginx'") | sort -u | crontab -

echo "Configuring firewall..."
systemctl enable firewalld
systemctl start firewalld
firewall-cmd --permanent --add-service=ssh
firewall-cmd --permanent --add-service=http
firewall-cmd --permanent --add-service=https
firewall-cmd --permanent --add-port=${DICOM_WORKLIST_PORT:-11112}/tcp
firewall-cmd --permanent --add-port=${DICOM_STORE_PORT:-11113}/tcp
firewall-cmd --reload

echo ""
echo "============================================="
echo " Deployment complete!"
echo "============================================="
supervisorctl status

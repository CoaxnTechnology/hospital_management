from .common import *
from pathlib import Path

# Load .env file
env_path = Path(BASE_DIR) / '.env'
if env_path.exists():
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, _, value = line.partition('=')
                os.environ.setdefault(key.strip(), value.strip())

DEBUG = os.environ.get('DEBUG', 'False').lower() in ('true', '1', 'yes')

ALLOWED_HOSTS = [
    os.environ.get('SUBDOMAIN', 'localhost'),
    os.environ.get('VPS_IP', '127.0.0.1'),
    'admin.clinicalgynecologists.space',
    'localhost',
    '127.0.0.1',
]

SECRET_KEY = os.environ.get('SECRET_KEY', ')s-7romvhcmfr^tyi0=owms#9(5#pj#s#so*yhz!t3_5tq)t&a')

ADMIN_DOMAIN = 'admin.clinicalgynecologists.space'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'echoapp'),
        'USER': os.environ.get('DB_USER', 'django'),
        'PASSWORD': os.environ.get('DB_PASS', 'Owbq4rT4_RqC'),
        'HOST': os.environ.get('DB_HOST', '127.0.0.1'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [(
                os.environ.get('REDIS_HOST', '127.0.0.1'),
                int(os.environ.get('REDIS_PORT', 6379)),
            )],
        },
    },
}

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.memcached.PyMemcacheCache",
        "LOCATION": "{}:{}".format(
            os.environ.get('MEMCACHED_HOST', '127.0.0.1'),
            os.environ.get('MEMCACHED_PORT', '11211'),
        ),
    },
    "select2": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://{}:{}/2".format(
            os.environ.get('REDIS_HOST', '127.0.0.1'),
            os.environ.get('REDIS_PORT', '6379'),
        ),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}

# Email (SMTP) — configure via .env
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', EMAIL_HOST_USER)

STATIC_ROOT = os.path.join(BASE_DIR, "public/static")

MEDIA_ROOT = os.path.abspath(os.path.join(BASE_DIR, "../", "data"))

# Security settings for HTTPS
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = True
SECURE_REDIRECT_EXEMPT = [r'^worklists/.*']
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

print('Using production settings')

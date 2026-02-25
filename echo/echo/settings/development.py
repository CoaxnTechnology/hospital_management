from .common import *

DEBUG = True

ALLOWED_HOSTS = ['0.0.0.0', 'localhost', '127.0.0.1', '*']

"""
INSTALLED_APPS += [
    'debug_toolbar',
]
MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
"""

if "POSTGRES_HOST" in os.environ:
    POSTGRES_HOST = os.environ["POSTGRES_HOST"]
else:
    POSTGRES_HOST = '127.0.0.1'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'echoapp',
        'USER': 'django',
        'PASSWORD': 'Owbq4rT4_RqC',
        'HOST': POSTGRES_HOST,
        'PORT': '5432',
    }
}

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("127.0.0.1", 6379)],
        },
    },
}

STATICFILES_DIRS = [os.path.join(BASE_DIR, "public/static")]

STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
#print(STATIC_ROOT)

MEDIA_ROOT = os.path.abspath(os.path.join(BASE_DIR, "../", "data"))

os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"

print('Using dev settings')
from .common import *

DEBUG = False

ALLOWED_HOSTS = ['0.0.0.0', 'localhost', '127.0.0.1', 'test.expert-echo.com', '164.90.221.1', '*']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'echoapp',
        'USER': 'django',
        'PASSWORD': 'Owbq4rT4_RqC',
        'HOST': '127.0.0.1',
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

STATIC_ROOT = "/home/vagrant/echo/public/static/"

MEDIA_ROOT = "/home/vagrant/data/"


print('Using test settings')
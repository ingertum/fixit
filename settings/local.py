from .base import *

ALLOWED_HOSTS = ['127.0.0.1', 'localhost']
DEBUG = True
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'dbxex.sqlite3'),
    }
}
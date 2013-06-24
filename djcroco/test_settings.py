DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

SECRET_KEY = 'lolz'

INSTALLED_APPS = (
    'djcroco.tests',
    'djcroco',
)

ROOT_URLCONF = 'djcroco.tests.urls'

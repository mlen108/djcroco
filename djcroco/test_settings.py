from django.conf.global_settings import TEMPLATE_CONTEXT_PROCESSORS

DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

TEMPLATE_DEBUG = DEBUG
TEMPLATE_CONTEXT_PROCESSORS += (
    'django.core.context_processors.request',
)

SECRET_KEY = 'lolz'

INSTALLED_APPS = (
    'djcroco.tests',
    'djcroco',
)

ROOT_URLCONF = 'djcroco.tests.urls'

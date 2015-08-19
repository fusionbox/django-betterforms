from __future__ import print_function
import os

SECRET_KEY = 'JVpuGfSgVm2IxJ03xArw5mwmPuYEzAJMbhsTnvLXOPSQR4z93o'

PROJECT_PATH = os.path.abspath(os.path.dirname(__file__))

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    # We need the SessionMiddleware for the WizardView support tests in Django >= 1.7
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
)

INSTALLED_APPS = (
    'django.contrib.sessions',
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'django.contrib.admin',
    'django.contrib.staticfiles',
    'tests',
    'betterforms',
)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'sqlite_database',
    }
}

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
    },
]

ROOT_URLCONF = 'tests.urls'

STATIC_URL = '/static/'
DEBUG = True

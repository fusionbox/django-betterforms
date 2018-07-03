DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'betterforms-tests.db',
    },
}

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.admin',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.staticfiles',
    'betterforms',
    'tests',
)

DEBUG = True

SECRET_KEY = 'JVpuGfSgVm2IxJ03xArw5mwmPuYEzAJMbhsTnvLXOPSQR4z93o'

SITE_ID = 1

ROOT_URLCONF = 'tests.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
    },
]

MIDDLEWARE = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
)
# Django 1.9 and earlier
MIDDLEWARE_CLASSES = MIDDLEWARE

STATIC_URL = '/static/'

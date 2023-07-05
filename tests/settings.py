import os

import django

try:
    from .local_settings import *  # noqa: F403
except ImportError:
    pass

BASE_PATH = os.path.join(os.path.dirname(__file__), "..")
SECRET_KEY = "EX-TER-MI-NA-TE"

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True
TIME_ZONE = "Europe/Paris"

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.staticfiles",
    "tests",
    "dalec_prime",
    "dalec",
    "dalec_caldav",
]

if django.VERSION < (3, 2):
    INSTALLED_APPS.append("django_jsonfield_backport")

ROOT_URLCONF = "tests.urls"

TEMPLATES = [
    {"BACKEND": "django.template.backends.django.DjangoTemplates", "APP_DIRS": True}
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_PATH, "tests.sqlite3"),
    }
}

DALEC_CALDAV_BASE_URL = "http://localhost:5232/test/"
DALEC_CALDAV_API_USERNAME = "test"
DALEC_CALDAV_API_PASSWORD = "test"
# For tests, we want ALL events (except for DALEC_EXTRA_CALDAV_URLS: it will be 365 days max)
DALEC_CALDAV_SERCH_EVENT_END_TIMEDELTA = None

try:
    # should be defined in local_settings
    DALEC_EXTRA_CALDAV_URLS  # noqa: F405
except NameError:
    DALEC_EXTRA_CALDAV_URLS = {
        # should be with this format:
        # "nextclould-v27": {
        #     "url": "https://nextcloud.example.com/index.php/apps/calendar/p/xxx/CalendarName",
        #     "username": "test",  # optionnal, only if this caldav needs authentication
        #     "password": "test",  # optionnal, only if this caldav needs authentication
        # }
    }

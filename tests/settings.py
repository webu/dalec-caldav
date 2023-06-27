import os

import django

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

DALEC_CALDAV_BASE_URL = (
    "http://localhost:5232/test/7eb24728-09c0-3977-4fca-e7bec231f7a0/"
)
DALEC_CALDAV_API_USERNAME = "test"
DALEC_CALDAV_API_PASSWORD = "test"

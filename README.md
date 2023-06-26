# 📅 dalec-caldav

[![Stable Version](https://img.shields.io/pypi/v/dalec-caldav?color=blue)](https://pypi.org/project/dalec-caldav/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)
[![semver](https://img.shields.io/badge/semver-2.0.0-green)](https://semver.org/)

Django Aggregate a Lot of External Content -- CalDav

Aggregate last event from a given CalDav instance.

Plugin of [🤖 dalec](https://github.com/webu/dalec).

## Installation

```
pip install dalec_caldav
```

In django settings `INSTALLED_APPS`, add:

```
INSTALLED_APPS = [
    ...
    "dalec",
    "dalec_prime",
    "dalec_caldav",
    ...
    ]
```


## Usage

General usage:
```django
{% load dalec %}

{% dalec "caldav" content_type [channel=None] [channel_object=None] [template=None] %}
```

### Events

Retrieves latest event of all calendars accessible for the current user:
```django
{% dalec "caldav" "event" %}
```

Retrieves latest event of a calendar defined by an url:
```django
{% dalec "caldav" "event" channel="url" channel_object="https://nextcloud.org/remote.php/dav/public-calendars/<calendarID>"%}
```


## Settings

Django settings must define:

  - `DALEC_CALDAV_BASE_URL` : CalDav instance url (ex: `https://caldav.org/`)
  - `DALEC_CALDAV_API_USERNAME` : CalDav username (ex: `admin`)
  - `DALEC_CALDAV_API_PASSWORD` : CalDav user password (ex: `azeazeaezdfqsmlkrjzr`)



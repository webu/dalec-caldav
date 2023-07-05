# 📅 dalec-caldav

[![Stable Version](https://img.shields.io/pypi/v/dalec-caldav?color=blue)](https://pypi.org/project/dalec-caldav/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)
[![semver](https://img.shields.io/badge/semver-2.0.0-green)](https://semver.org/)
[![Documentation Status](https://readthedocs.org/projects/dalec-caldav/badge/?version=latest)](https://dalec-caldav.readthedocs.io/en/latest/?badge=latest)

Django Aggregate a Lot of External Content -- CalDav

Aggregate last event from a given CalDav instance.

Plugin of [🤖 dalec](https://github.com/webu/dalec).

## Installation

```
pip install dalec-caldav
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

{% dalec "caldav" content_type [channel=None] [channel_object=None] [template=None] [ordered_by=None] %}
```

### Events

Retrieves latest updated events of all calendars accessible for the current user:
```django
{% dalec "caldav" "event" %}
```

Retrieves latest updated events of a calendar defined by an url:
```django
{% dalec "caldav" "event" channel="url" channel_object="https://nextcloud.org/remote.php/dav/public-calendars/<calendarID>" %}
```


## Settings

Django settings must define:

  - `DALEC_CALDAV_BASE_URL`: CalDav instance url (ex: `https://caldav.org/`)
  - `DALEC_CALDAV_API_USERNAME`: CalDav username (ex: `admin`)
  - `DALEC_CALDAV_API_PASSWORD`: CalDav user password (ex: `azeazeaezdfqsmlkrjzr`)

Some other settings are optionnal:

### `DALEC_CALDAV_SERCH_EVENT_START_TIMEDELTA`

Default to `timedelta(days=-1)`. When fetching events from calendar, only events that are newer
from this timedelta will be retrieved. It avoid to retrieve a huge amount of past events. 

### `DALEC_CALDAV_SERCH_EVENT_END_TIMEDELTA`

Default to `timedelta(days=365)`. When fetching events from calendar, only events that are older
from this timedelta will be retrieved. It avoid to retrieve a huge amount of past events. 

## Tests

This dalec uses [Radicale](https://radicale.org/) as tiny python caldav server wich can runs 
inside tox out of the box. 
If you want to test with other caldavs servers, you can add a `local_settings.py` file in 
`tests/` folder and add a dict conf of extra calendars `DALEC_EXTRA_CALDAV_URLS`:

```python
DALEC_EXTRA_CALDAV_URLS = {
    "nextclould-v27-public": {
        "url": "https://nextcloud.example.com/remote.php/dav/public-calendars/saiGzyBYcWct24W8/",
    },
    "nextclould-v27-auth": {
        "url": "https://nextcloud.example.com/remote.php/dav/calendars/username/calendarname/",
        "username": "username",
        "password": "secret",
    },
    "my-other-caldav-events": {
        "url": "https://caldav.example.com/xxx/",
    },
}
```

This will perform simple test to check the proxy seems to work with this type of caldav server: 

- try to fetch events 
- assert there is at least 1 event fetched.

If your calendar has no event, test will fail.

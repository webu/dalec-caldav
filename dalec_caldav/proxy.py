# Future imports
from __future__ import annotations

# Standard libs
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import date
    from typing import Dict, Any, List
    from vobject.base import Component
    from caldav.objects import Calendar, CalendarObjectResource

from datetime import datetime, timedelta
from urllib.parse import urlparse

# Django imports
from django.conf import settings
from django.utils.timezone import make_aware, now


# DALEC imports
from caldav.davclient import DAVClient
from caldav.elements import dav
from caldav.objects import Event
from dalec import settings as app_settings
from dalec.proxy import Proxy

client = DAVClient(
    url=settings.DALEC_CALDAV_BASE_URL,
    username=settings.DALEC_CALDAV_API_USERNAME,
    password=settings.DALEC_CALDAV_API_PASSWORD,
)


class CaldavProxy(Proxy):
    """
    caldav dalec proxy to fetch the last event.
    """

    app = "caldav"

    def _fetch(
        self, nb: int, content_type: str, channel: str, channel_object: str
    ) -> Dict[str, dict]:
        if content_type == "event":
            return self._fetch_event(nb, channel, channel_object)
        raise ValueError(f"Invalid content_type {content_type}. Accepted: event.")

    def _fetch_event(self, nb: int, channel: str, channel_object: str) -> Dict[str, dict]:
        """
        Get latest events from calendar(s)
        """

        if channel == "url" and channel_object:
            if channel_object[-1] != "/":
                channel_object += "/"
            calendars = client.calendar(url=channel_object)
            if type(calendars) != list:
                calendars = [calendars]
        else:
            principal = client.principal()
            calendars = principal.calendars()

        contents = {}
        for calendar in calendars:
            calendar_infos = self._get_calendar_infos(calendar)
            for event in self._get_events(calendar):
                content = self._populate_content(event, calendar_infos)
                contents[content["id"]] = content
        return contents

    def _get_events(self, calendar: Calendar) -> List[CalendarObjectResource]:
        start_td = app_settings.get_setting(
            "CALDAV_SERCH_EVENT_START_TIMEDELTA", timedelta(days=-1)
        )
        end_td = app_settings.get_setting(
            "CALDAV_SERCH_EVENT_END_TIMEDELTA", timedelta(days=365)
        )
        search_kwargs = {
            "comp_class": Event,
            "start": now() + start_td if start_td is not None else None,
            "end": now() + end_td if end_td is not None else None,
        }
        return calendar.search(**search_kwargs)

    def _get_calendar_infos(self, calendar: Calendar) -> Dict[str, Any]:
        url = str(calendar.url)
        infos = {
            "type": "default",
            "display_name": calendar.get_property(dav.DisplayName()),
            "url": url,
        }
        if "/remote.php/dav/public-calendars/" in url:
            url_obj = urlparse(url)
            token = url_obj.path.split("/")[-2]
            nextcloud_calendar_url = "{}://{}/index.php/apps/calendar/p/{}".format(
                url_obj.scheme, url_obj.netloc, token
            )
            infos.update(
                {
                    "type": "nextcloud",
                    "nextcloud_calendar_url": nextcloud_calendar_url,
                    "token": token,
                }
            )
        return infos

    def _vobject_to_dict(
        self, vobject: Component
    ) -> Dict[str, Any[str, int, datetime, date]]:
        content = {}
        for key, val in vobject.contents.items():
            if hasattr(val[0], "contents"):
                content[key] = self._vobject_to_dict(val[0])
            else:
                content[key] = val[0].value
        return content

    def _populate_content(self, event: Event, calendar_infos: Dict[str, Any]) -> dict:
        content = self._vobject_to_dict(event.vobject_instance.vevent)
        content["event_url"] = event.canonical_url
        content["dav_calendar_url"] = calendar_infos["url"]
        content["calendar_displayname"] = calendar_infos["display_name"]
        if "created" not in content:
            # some events accepted from an email in thunderbird can be without created info
            dates = []
            if "dtstamp" in content:
                dates.append(
                    make_aware(content["dtstamp"])
                    if not content["dtstamp"].tzinfo
                    else content["dtstamp"]
                )
            if "last-modified" in content:
                dates.append(
                    make_aware(content["last-modified"])
                    if not content["last-modified"].tzinfo
                    else content["last-modified"]
                )
            content["created"] = min(dates) if dates else None
        if "last-modified" not in content:
            content["last-modified"] = content["created"]
        if calendar_infos["type"] == "nextcloud":
            content["nextcloud_calendar_url"] = calendar_infos["nextcloud_calendar_url"]
        duration = event.get_duration()
        content.update(
            {
                "id": content["uid"],
                "creation_dt": (
                    make_aware(content["created"])
                    if not content["created"].tzinfo
                    else content["created"]
                ),
                "last_update_dt": (
                    make_aware(content["last-modified"])
                    if not content["last-modified"].tzinfo
                    else content["last-modified"]
                ),
                "duration": {
                    "days": duration.days,
                    "seconds": duration.seconds,
                    "total_seconds": int(duration.total_seconds()),
                },
            }
        )
        if isinstance(content["dtstart"], datetime):
            content["start_date"] = content["dtstart"].date()
            content["start_time"] = content["dtstart"].time()
        else:
            content["start_date"] = content["dtstart"]
            content["start_time"] = None
        if isinstance(content["dtend"], datetime):
            content["end_date"] = content["dtend"].date()
            content["end_time"] = content["dtend"].time()
        else:
            content["end_date"] = content["dtend"]
            content["end_time"] = None
        return content

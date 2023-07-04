# Future imports
from __future__ import annotations

# Standard libs
from datetime import datetime
from typing import TYPE_CHECKING
from urllib.parse import urlparse

if TYPE_CHECKING:
    from typing import Dict, Any
    from caldav.objects import Calendar, Event

# Django imports
from django.conf import settings

# DALEC imports
from caldav import DAVClient
from caldav import dav
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
            for event in calendar.events():
                content = self._populate_content(event, calendar_infos)
                contents[content["id"]] = content
        return contents

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
                    "nextcloud_calendar_url": nextcloud_calendar_url,
                    "token": token,
                }
            )
        return infos

    def _populate_content(self, event: Event, calendar_infos: Dict[str, Any]) -> dict:
        content = {
            key: val[0].value for key, val in event.vobject_instance.vevent.contents.items()
        }
        content["event_url"] = str(event.url)
        content["dav_calendar_url"] = calendar_infos["url"]
        content["calendar_displayname"] = calendar_infos["display_name"]

        if calendar_infos["type"] == "nextcloud":
            content["nextcloud_calendar_url"] = calendar_infos["nextcloud_calendar_url"]
        duration = content["dtend"] - content["dtstart"]
        content.update(
            {
                "id": str(event.vobject_instance.vevent.contents["uid"][0].value),
                "creation_dt": content["created"],
                "last_update_dt": content["last-modified"],
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

from datetime import timedelta
from typing import Dict
import requests
from urllib.parse import urlparse

from django.utils.dateparse import parse_datetime
from django.utils.timezone import now
from django.conf import settings

from dalec.proxy import Proxy

from caldav import DAVClient, dav

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

        raise ValueError(f"Invalid content_type {content_type}. Accepted: event." )

    def _fetch_event(self, nb, channel=None, channel_object=None):
        """
        Get latest event from calendar
        """
        options = {
                "per_page": nb,
                }

        if channel == "url":
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
            calendar_displayname = calendar.get_property(dav.DisplayName())
            calendar_url = calendar.url.url_raw

            for event in calendar.events():
                id = str(event.vobject_instance.vevent.contents["uid"][0].value)
                content = {
                        key: val[0].value
                        for key, val
                        in event.vobject_instance.vevent.contents.items()
                        }
                content["event_url"] = str(event.url)
                content["dav_calendar_url"] = calendar_url
                content["calendar_displayname"] = calendar_displayname

                res = urlparse(calendar.url.url_raw)
                if ( "/remote.php/dav/public-calendars/" in res.path):
                    # seems to be nextcloud
                    token = res.path.split("/")[-1]
                    nextcloud_calendar_url = "{}://{}/index.php/apps/calendar/p/{}".format(
                        res.scheme, res.netloc, token
                    )
                    content["nextcloud_calendar_url"] = nextcloud_calendar_url

                contents[id] = {
                        **content,
                        "id": id,
                        "creation_dt": content["created"],
                        "last_update_dt": now()
                        }
        return contents

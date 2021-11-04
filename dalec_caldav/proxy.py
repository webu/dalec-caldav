from datetime import timedelta
from typing import Dict
import requests

from django.utils.dateparse import parse_datetime
from django.utils.timezone import now
from django.conf import settings

from dalec.proxy import Proxy

from caldav import DAVClient

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

        raise ValueError(f"Invalid content_type {content_type}. Accepted: topic, category." )

    def _fetch_event(self, nb, channel=None, channel_object=None):
        """
        Get latest event from calendar
        """
        options = {
                "per_page": nb,
                }

        # TODO

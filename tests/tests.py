from datetime import timedelta
from importlib import reload
from unittest import skipIf

from bs4 import BeautifulSoup
from django.conf import settings
from django.template import Context, Template
from django.test import Client, TestCase
from django.urls import reverse
from requests.exceptions import ConnectionError

from dalec.proxy import ProxyPool
from dalec.tests_utils import DalecTestCaseMixin
from dalec_caldav import proxy

__all__ = ["DalecTests"]


class DalecTests(DalecTestCaseMixin, TestCase):
    def _cal_url(self, cal):
        if cal == "primary":
            cal = "7eb24728-09c0-3977-4fca-e7bec231f7a0"
        elif cal == "secondary":
            cal = "4fc45ea4-371e-81ab-ee54-295eb8ec28a6"
        return "%s/%s" % (settings.DALEC_CALDAV_BASE_URL, cal)

    def test_caldav_with_wrong_url(self):
        wrong_url = "https://doesnoexist.dalec.webu.coop/"
        with self.settings(DALEC_CALDAV_BASE_URL=wrong_url):
            ProxyPool.unregister("caldav")
            reload(proxy)
            dalec_caldav = ProxyPool.get("caldav")
            with self.assertRaises(ConnectionError):
                dalec_caldav.refresh(
                    content_type="event",
                    channel="url",
                    channel_object=wrong_url,
                    force=True,
                )
        ProxyPool.unregister("caldav")
        reload(proxy)

    def test_retrieve_events_from_multiple_calendars(self):
        kwargs = {"app": "caldav", "content_type": "event", "channel": "url"}
        url = reverse("dalec_fetch_content", kwargs=kwargs)
        client = Client()
        response = client.post(
            url,
            # no channel objects: lets fetch events from all calendars
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        qs = self.content_model.objects.filter(
            app="caldav",
            content_type="event",
            channel="url",
        )
        self.assertEqual(qs.count(), 6)
        contents = dict((c.content_id.split("-", 1)[0], c) for c in qs)
        self.assertIn("88bb03ce", contents)
        self.assertEqual(contents["88bb03ce"].content_data["calendar_displayname"], "Secondary")
        self.assertIn("0239cc8f", contents)
        self.assertEqual(contents["0239cc8f"].content_data["calendar_displayname"], "Primary")
        self.assertIn("04bbb7da", contents)
        self.assertIn("f54e19f1", contents)
        self.assertIn("b843d43a", contents)
        self.assertIn("8c6c5b2d", contents)

        # check events are returned in default order (last_updated first)
        orig_keys = [k for k in contents.keys()]
        expect_keys = [
            c.content_id.split("-", 1)[0]
            for c in sorted(contents.values(), key=lambda c: c.last_update_dt, reverse=True)
        ]
        self.assertEqual(orig_keys, expect_keys)

    def test_retrieve_events_from_unique_calendars(self):
        kwargs = {"app": "caldav", "content_type": "event", "channel": "url"}
        url = reverse("dalec_fetch_content", kwargs=kwargs)
        client = Client()
        response = client.post(
            url,
            '{"channelObjects": ["%s"]}' % self._cal_url("secondary"),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        qs = self.content_model.objects.filter(
            app="caldav",
            content_type="event",
            channel="url",
        )
        self.assertEqual(qs.count(), 1)
        contents = dict((c.content_id.split("-", 1)[0], c) for c in qs)
        self.assertIn("88bb03ce", contents)
        self.assertEqual(contents["88bb03ce"].content_data["calendar_displayname"], "Secondary")

    def test_dates(self):
        kwargs = {"app": "caldav", "content_type": "event", "channel": "url"}
        url = reverse("dalec_fetch_content", kwargs=kwargs)
        client = Client()
        response = client.post(
            url,
            '{"channelObjects": ["%s"]}' % self._cal_url("primary"),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        qs = self.content_model.objects.filter(
            app="caldav",
            content_type="event",
            channel="url",
            channel_object=self._cal_url("primary"),
        )
        self.assertEqual(qs.count(), 5)
        contents = dict((c.content_id.split("-", 1)[0], c) for c in qs)
        # event on 2 days, without hours
        self.assertEqual(contents["0239cc8f"].content_data["duration"]["days"], 2)
        self.assertIsNone(contents["0239cc8f"].content_data["start_time"])
        self.assertIsNone(contents["0239cc8f"].content_data["end_time"])
        self.assertEqual(contents["0239cc8f"].content_data["start_date"], "2035-07-04")
        self.assertEqual(contents["0239cc8f"].content_data["end_date"], "2035-07-06")

        # event on 1 day, without hours
        self.assertEqual(contents["04bbb7da"].content_data["duration"]["days"], 1)
        self.assertIsNone(contents["04bbb7da"].content_data["start_time"])
        self.assertIsNone(contents["04bbb7da"].content_data["end_time"])
        self.assertEqual(contents["04bbb7da"].content_data["start_date"], "2035-07-02")
        self.assertEqual(contents["04bbb7da"].content_data["end_date"], "2035-07-03")

        # event on 9+ days, with hours
        self.assertEqual(contents["f54e19f1"].content_data["duration"]["days"], 9)
        self.assertEqual(contents["f54e19f1"].content_data["duration"]["seconds"], 14400)
        self.assertEqual(contents["f54e19f1"].content_data["duration"]["total_seconds"], 792000)
        self.assertEqual(contents["f54e19f1"].content_data["start_time"], "20:10:00")
        self.assertEqual(contents["f54e19f1"].content_data["end_time"], "00:10:00")
        self.assertEqual(contents["f54e19f1"].content_data["start_date"], "2030-10-10")
        self.assertEqual(contents["f54e19f1"].content_data["end_date"], "2030-10-20")

        # event for some hours
        self.assertEqual(contents["8c6c5b2d"].content_data["duration"]["days"], 0)
        self.assertEqual(contents["8c6c5b2d"].content_data["duration"]["seconds"], 2520)
        self.assertEqual(contents["8c6c5b2d"].content_data["duration"]["total_seconds"], 2520)
        self.assertEqual(contents["8c6c5b2d"].content_data["start_time"], "00:42:00")
        self.assertEqual(contents["8c6c5b2d"].content_data["end_time"], "01:24:00")
        self.assertEqual(contents["8c6c5b2d"].content_data["start_date"], "2042-02-11")
        self.assertEqual(contents["8c6c5b2d"].content_data["end_date"], "2042-02-11")

    def test_dates_in_template(self):
        # load contents
        kwargs = {
            "app": "caldav",
            "content_type": "event",
            "channel": "url",
            "ordered_by": "dtstart",
        }
        url = reverse("dalec_fetch_content", kwargs=kwargs)
        client = Client()
        response = client.post(
            url,
            '{"channelObjects": ["%s"]}' % self._cal_url("primary"),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)

        t = Template(
            """
            {% load dalec %}
            {% dalec "caldav" "event" channel="url" channel_object=url ordered_by="dtstart" %}
        """
        )
        output = t.render(Context({"url": self._cal_url("primary")}))
        soup = BeautifulSoup(output, "html.parser")
        dalec_divs = soup.find_all(class_="dalec-item")
        date_divs = soup.find_all(class_="caldav-item-dates")
        self.assertEqual(len(date_divs), 5)

        times = dalec_divs[0].find_all("time")
        self.assertEqual(len(times), 2)
        self.assertEqual(times[0]["datetime"], "2030-10-10T20:10:00+02:00")
        self.assertEqual(times[1]["datetime"], "2030-10-20T00:10:00+02:00")

        times = dalec_divs[1].find_all("time")
        self.assertEqual(len(times), 1)
        self.assertEqual(times[0]["datetime"], "2035-07-02")

        times = dalec_divs[2].find_all("time")
        self.assertEqual(len(times), 2)
        self.assertEqual(times[0]["datetime"], "2035-07-04")
        self.assertEqual(times[1]["datetime"], "2035-07-06")

        times = dalec_divs[4].find_all("time")
        self.assertEqual(len(times), 2)
        self.assertEqual(times[0]["datetime"], "2042-02-11T00:42:00+01:00")
        self.assertEqual(times[1]["datetime"], "2042-02-11T01:24:00+01:00")

    @skipIf(
        bool(settings.DALEC_EXTRA_CALDAV_URLS) is False,
        "no extra caldavs to test. see README and local_settings.py if you want to",
    )
    def test_retrieve_events_from_other_caldavs(self):
        for name, conf in settings.DALEC_EXTRA_CALDAV_URLS.items():
            ProxyPool.unregister("caldav")
            new_settings = {
                "DALEC_CALDAV_BASE_URL": conf["url"],
                "DALEC_CALDAV_API_USERNAME": conf.get("username"),
                "DALEC_CALDAV_API_PASSWORD": conf.get("password"),
                "DALEC_CALDAV_SERCH_EVENT_END_TIMEDELTA": timedelta(days=365),
            }
            with self.settings(**new_settings):
                reload(proxy)
                dalec_caldav = ProxyPool.get("caldav")
            try:
                nb_created, nb_updated, nb_deleted = dalec_caldav.refresh(
                    content_type="event",
                    channel="url",
                    channel_object=conf["url"],
                    force=True,
                )
            except Exception as e:
                raise Exception("%s error: %s" % (name, e)) from e
            qs = self.content_model.objects.filter(
                app="caldav",
                content_type="event",
                channel="url",
                channel_object=conf["url"],
            )
            self.assertTrue(qs.exists())
            self.assertGreaterEqual(nb_created, 1)
            self.assertEqual(nb_updated, 0)
            self.assertGreaterEqual(nb_created, qs.count())
        ProxyPool.unregister("caldav")
        reload(proxy)

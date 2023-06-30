from bs4 import BeautifulSoup
from django.conf import settings
from django.template import Context, Template
from django.test import Client, TestCase
from django.urls import reverse

from dalec.tests_utils import DalecTestCaseMixin

__all__ = ["DalecTests"]


class DalecTests(DalecTestCaseMixin, TestCase):
    radical_calendar_url = settings.DALEC_CALDAV_BASE_URL

    def test_retrieve_events(self):
        kwargs = {"app": "caldav", "content_type": "event", "channel": "url"}
        url = reverse("dalec_fetch_content", kwargs=kwargs)
        client = Client()
        response = client.post(
            url,
            '{"channelObjects": ["%s"]}' % self.radical_calendar_url,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        qs = self.content_model.objects.filter(
            app="caldav",
            content_type="event",
            channel="url",
            channel_object=self.radical_calendar_url,
        )
        self.assertEqual(qs.count(), 5)
        contents = dict((c.content_id.split("-", 1)[0], c) for c in qs)
        self.assertIn("0239cc8f", contents)
        self.assertIn("04bbb7da", contents)
        self.assertIn("f54e19f1", contents)
        self.assertIn("b843d43a", contents)
        self.assertIn("8c6c5b2d", contents)

        # check events are returned in default order (last_updated first)
        orig_keys = [k for k in contents.keys()]
        expect_keys = [
            c.content_id.split("-", 1)[0]
            for c in sorted(
                contents.values(), key=lambda c: c.last_update_dt, reverse=True
            )
        ]
        self.assertEqual(orig_keys, expect_keys)

    def test_dates(self):
        kwargs = {"app": "caldav", "content_type": "event", "channel": "url"}
        url = reverse("dalec_fetch_content", kwargs=kwargs)
        client = Client()
        response = client.post(
            url,
            '{"channelObjects": ["%s"]}' % self.radical_calendar_url,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        qs = self.content_model.objects.filter(
            app="caldav",
            content_type="event",
            channel="url",
            channel_object=self.radical_calendar_url,
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
        self.assertEqual(
            contents["f54e19f1"].content_data["duration"]["seconds"], 14400
        )
        self.assertEqual(
            contents["f54e19f1"].content_data["duration"]["total_seconds"], 792000
        )
        self.assertEqual(contents["f54e19f1"].content_data["start_time"], "20:10:00")
        self.assertEqual(contents["f54e19f1"].content_data["end_time"], "00:10:00")
        self.assertEqual(contents["f54e19f1"].content_data["start_date"], "2030-10-10")
        self.assertEqual(contents["f54e19f1"].content_data["end_date"], "2030-10-20")

        # event for some hours
        self.assertEqual(contents["8c6c5b2d"].content_data["duration"]["days"], 0)
        self.assertEqual(contents["8c6c5b2d"].content_data["duration"]["seconds"], 2520)
        self.assertEqual(
            contents["8c6c5b2d"].content_data["duration"]["total_seconds"], 2520
        )
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
            '{"channelObjects": ["%s"]}' % self.radical_calendar_url,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)

        t = Template(
            """
            {% load dalec %}
            {% dalec "caldav" "event" channel="url" channel_object=url ordered_by="dtstart" %}
        """
        )
        output = t.render(Context({"url": self.radical_calendar_url}))
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

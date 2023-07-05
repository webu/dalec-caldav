# Content returned by dalec_caldav

Every dalec save in database object with the following attributes:

 - `last_update_dt` 
 - `creation_dt` 
 - `app` 
 - `content_type` 
 - `channel` 
 - `channel_object` 
 - `dj_channel_content_type_id`
 - `dj_channel_id`
 - `dj_content_content_type_id`
 - `dj_content_id`
 - `content_id`
 - `content_data`

See [the main dalec](https://github.com/webu/dalec) repository for more information.
Hereafter are detailed the `content_data`, specific to the `caldav` content type.

## Event

It retrieves event contents. It also try to retrieve full url if it "seems to be" a nextcloud url.

`"key": "value"` is a placeholder and represent every content in the vevent contents of your calendar

```python
{
 "key": "value",
 "event_url": "https://caldav.org/event_url",
 "dav_calendar_url": "calendar_url",
 "calendar_displayname": "My Calendar",
 "nextcloud_calendar_url": "https://nextcloud.org/index.php/apps/calendar/p/TOKEN",
 "id": "uuid of this event",
 "creation_dt": "2019-10-02T09:56:40.296Z",
 "last_update_dt": "2019-10-02T09:56:40.296Z",
 "duration": {
     "days": 1,
     "seconds": 0,
     "total_seconds": 86400,
 },
 "start_date": "2019-10-02",
 "start_time": "09:00:00",
 "end_date": "2019-10-03",
 "end_time": "09:00:00"
}
```

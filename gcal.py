from Google import Create_Service, convert_to_RFC_datetime
from dateutil.parser import parse as dtparse
from datetime import datetime as dt

CLIENT_SECRET_FILE = 'clientjson.json'
API_NAME = 'calendar'
API_VERSION = 'v3'
SCOPES = ['https://www.googleapis.com/auth/calendar']

service = Create_Service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)


# create event
def create_event_google(name, year, month, day, hour, minute):
    event_request_body = {
        'start': {
            'dateTime': convert_to_RFC_datetime(year, month, day, hour, minute),
            'timeZone': 'Asia/Singapore'
        },
        'end': {
            'dateTime': convert_to_RFC_datetime(year, month, day, hour + 2, minute),
            'timeZone': 'Asia/Singapore'
        },
        'summary': name,
        'status': 'confirmed',
        'transparency': 'opaque',
        'visibility': 'private',
    }

    response = service.events().insert(
        calendarId="primary",
        body=event_request_body
    ).execute()
    return response['id']


def update_event_google(event_id, name, year, month, day, hour, minute):
    event_request_body = {
        'start': {
            'dateTime': convert_to_RFC_datetime(year, month, day, hour, minute),
            'timeZone': 'Asia/Singapore'
        },
        'end': {
            'dateTime': convert_to_RFC_datetime(year, month, day, hour + 2, minute),
            'timeZone': 'Asia/Singapore'
        },
        'summary': name,
        'status': 'confirmed',
        'transparency': 'opaque',
        'visibility': 'private',
    }
    service.events().update(calendarId='primary', eventId=event_id, body=event_request_body).execute()


def delete_event_google(event_id):
    service.events().delete(calendarId="primary", eventId=event_id).execute()


def read_google_events():
    tmfmt = '%d %m %Y, %H%M'

    r = service.events().list(calendarId="primary").execute()
    events = r.get('items')
    event_dict_list = []
    for event in events:
        if "dateTime" in event['start']:
            start = event['start']['dateTime']
            stime = dt.strftime(dtparse(start), format=tmfmt)
            day = int(stime[:2])
            month = int(stime[3:5])
            year = int(stime[6:10])
            time = stime[-4:]
            if dt(day=day, month=month, year=year) >= dt.today():
                event_id = event['id']
                name = event['summary']
                event_dict = {'name': name, 'day': day, 'month': month, 'year': year, 'time': time,
                              'event_id': event_id}
                event_dict_list.append(event_dict)
    return event_dict_list

# def delete_event_google():
#     service.events().delete(calendarId="primary", eventId=).execute()

from re import match
import dateutil.parser
from mwparserfromhell.nodes import Template
from pytz import timezone
from .wiki_time import WikiTime


def parse_str(timestamp: str, tz: timezone = None):
    timestamp_parsed = dateutil.parser.parse(timestamp)
    return WikiTime(timestamp_parsed, tz=tz)


def parse_template(template: Template):
    """
    Pulls date-time information encoded by a template and returns a WikiTime object.
    If date-time information is missing or incomplete, None is returned instead.
    
    :param template: A mwparserfromhell Template object with date, time, and timezone parameters
    :return: a WikiTime object representing the date-time information encoded by this template
    """
    tz_lookup = {
        'PST': WikiTime.pst,
        'CET': WikiTime.cet,
        'KST': WikiTime.kst
    }
    if not template.has('date') or not template.has('time'):
        return None
    date = template.get("date").value.strip()
    time = template.get("time").value.strip()
    if date == '' or time == '':
        return None

    # Fix case of a time being written as 100 or 1100 without a :
    if match(r'\d\d\d\d', time):
        time = '{}:{}'.format(time[:2], time[3:])
    elif match(r'\d\d\d', time):
        time = '{}:{}'.format(time[:1], time[2:])

    tz_local_str = template.get('timezone').value.strip()
    tz_local = tz_lookup[tz_local_str]
    date_and_time = date + " " + time
    return WikiTime(date_and_time, tz=tz_lookup[tz_local])

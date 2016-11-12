from datetime import datetime, date, time, timedelta
from .models import EventType


# temporal useful functions
# -------------------------------------------------------------------------------
def time_delta_total_seconds(time_delta):
    """
    Calculate the total number of seconds represented by a 
    ``datetime.timedelta`` object
    
    """
    return time_delta.days * 3600 + time_delta.seconds


def tomorrow_morning():
    return datetime.combine(date.today()+timedelta(days=+1), time.min)


def tomorrow_evening():
    return datetime.combine(date.today()+timedelta(days=+1), time.max)


def end_of_next_days(duration=3):
    end_day = date.today()+timedelta(days=+duration)
    return datetime.combine(end_day, time.max)


def list_days(start_time, end_time):
    """
    :param start_time:
    :param end_time:
    :return: list of datetimes corresponding to days
    """
    diff = end_time - start_time
    return [start_time + timedelta(days=+i) for i in range(diff.days + 1)]


def construct_time(day, hour):
    return datetime.combine(day, hour)


def construct_day(year, month, day):
    return date(int(year), int(month), int(day))


def construct_hour(hour_string):
    number = hour_string.split('h')
    return time(hour=int(number[0]), minute=int(number[1]))


def construct_hour_string(datetime_hour):
    hour = "%02d" % datetime_hour.hour
    minutes = "%02d" % datetime_hour.minute
    return "h".join([hour, minutes])


# management of event_types useful functions
# -------------------------------------------------------------------------------

def get_event_type_list(event_type_id_string, current_topic):
    """unsplit event_type_list_string such as 1&2&3 into event_type_id and return corresponding EventTypes"""
    id_list = [int(i) for i in event_type_id_string.split('&')]
    return EventType.objects.filter(id__in=id_list,
                                    topic=current_topic)


def create_id_string(object_list):
    return '&'.join([str(thing.id) for thing in object_list])

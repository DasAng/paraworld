import datetime

def datetimeConverter(o):
    if isinstance(o, datetime.datetime):
        return o.__str__()
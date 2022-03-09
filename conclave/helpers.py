import datetime

def datetimeConverter(o):
    if isinstance(o, datetime.datetime):
        return o.__str__()

def excludeKeys(d, keys):
    return {x: d[x] for x in d if x not in keys}
from datetime import datetime


def timestamp_converter(timestamp):
    if not isinstance(timestamp, int):
        return None
    try:
        time = datetime.fromtimestamp(timestamp).strftime("%H:%M")
        return time
    except ValueError:
        return None

from datetime import datetime, timezone
import zoneinfo
import pytz

# on Windows pip install tzdata

utc = pytz.utc

def utc_to_est(origin: datetime):
    utc_time = datetime(origin.year, origin.month, origin.day, origin.hour, origin.minute, origin.second, tzinfo=utc)
    est = zoneinfo.ZoneInfo('America/New_York')
    est_time = utc_time.astimezone(est)
    return est_time
from datetime import datetime, timezone
import zoneinfo
# on Windows pip install tzdata


utc_time = datetime.now()
print(f'UTC: {utc_time}')
est = zoneinfo.ZoneInfo('America/New_York')
est_time = utc_time.astimezone(est)
print(f'EST: {est_time}')

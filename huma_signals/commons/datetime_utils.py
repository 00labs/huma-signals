import datetime


def tz_aware_utc_now() -> datetime.datetime:
    return datetime.datetime.now(tz=datetime.timezone.utc)

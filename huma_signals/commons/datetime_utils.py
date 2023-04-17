import datetime


def timestamp_to_tz_aware_utc_datetime(timestamp: int | str) -> datetime.datetime:
    tz_naive_dt = datetime.datetime.fromtimestamp(int(timestamp))
    return tz_naive_dt.astimezone(datetime.timezone.utc)


def tz_aware_utc_now() -> datetime.datetime:
    return datetime.datetime.now(tz=datetime.timezone.utc)

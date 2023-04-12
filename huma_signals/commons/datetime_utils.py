import datetime


def tz_aware_utc_now() -> datetime.datetime:
    return datetime.datetime.now(tz=datetime.timezone.utc)


def date_to_month_str(d: datetime.date) -> str:
    """
    Transforms a date object into a YYYY-MM formatted string for the month.
    """
    return d.strftime("%Y-%m")

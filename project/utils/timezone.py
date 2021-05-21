from django.utils import timezone


def round_time(value):
    return value.replace(second=0, microsecond=0)


def rounded_localtime():
    return round_time(timezone.localtime())


def rounded_now():
    return round_time(timezone.now())

from datetime import UTC, datetime

from apscheduler.triggers.cron import CronTrigger

from app.config import settings


def check_trigger() -> CronTrigger:
    """The cron trigger the worker uses to queue scheduled checks."""
    return CronTrigger.from_crontab(settings.schedule_cron)


def next_check_at() -> datetime | None:
    return check_trigger().get_next_fire_time(None, datetime.now(UTC))

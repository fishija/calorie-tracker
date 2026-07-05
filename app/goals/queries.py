from datetime import datetime, timedelta, timezone
from app.models import Goal
from app.db import db


def _today_utc_range() -> tuple[datetime, datetime]:
    start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    end = start + timedelta(days=1)
    return start, end


def get_todays_goal(user_id: int) -> Goal | None:
    start, end = _today_utc_range()
    return (
        Goal.query.filter(
            Goal.user_id == user_id,
            Goal.effective_date >= start,
            Goal.effective_date < end
        ).first()
    )

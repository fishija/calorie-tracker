from datetime import datetime, timedelta, timezone, date as date_type
from app.models import Goal
from app.db import db


def _utc_range_for_date(target_date: date_type) -> tuple[datetime, datetime]:
    start = datetime.combine(target_date, datetime.min.time(), tzinfo=timezone.utc)
    end = start + timedelta(days=1)
    return start, end


def get_todays_goal(user_id: int) -> Goal | None:
    start, end = _utc_range_for_date(date_type.today())
    return (
        Goal.query.filter(
            Goal.user_id == user_id,
            Goal.effective_date >= start,
            Goal.effective_date < end
        ).first()
    )


def get_goal_for_date(user_id: int, selected_date: date_type) -> Goal | None:
    start, end = _utc_range_for_date(selected_date)

    # Get latest goal that is effective on or before the target date
    goal = (
        Goal.query.filter(
            Goal.user_id == user_id,
            Goal.effective_date <= end,
        ).order_by(Goal.effective_date.desc())
        .first()
    )

    # If no such goal exists, search for the earliest goal that is effective after the target date
    if goal is None:
        goal = (
            Goal.query.filter(
                Goal.user_id == user_id,
                Goal.effective_date > start,
            ).order_by(Goal.effective_date.asc())
            .first()
        )

    # If no goal is found, return None
    return goal

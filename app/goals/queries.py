from datetime import date as date_type
from app.models import Goal
from app.db import db


def get_todays_goal(user_id: int) -> Goal | None:
    goal = (
        Goal.query.filter(
            Goal.user_id == user_id,
            Goal.effective_date == date_type.today(),
        ).order_by(Goal.effective_date.desc())
        .first()
    )
    return goal


def get_goal_for_date(user_id: int, selected_date: date_type) -> Goal | None:
    # Get latest goal that is effective on or before the target date
    goal = (
        Goal.query.filter(
            Goal.user_id == user_id,
            Goal.effective_date <= selected_date,
        ).order_by(Goal.effective_date.desc())
        .first()
    )

    # If no such goal exists, search for the earliest goal that is effective after the target date
    if goal is None:
        goal = (
            Goal.query.filter(
                Goal.user_id == user_id,
                Goal.effective_date > selected_date,
            ).order_by(Goal.effective_date.asc())
            .first()
        )

    # If no goal is found, return None
    return goal

"""Goal queries for retrieving user nutritional goals."""

from datetime import date
from app.models import Goal


def get_todays_goal(user_id: int) -> Goal | None:
    """Retrieve today's nutritional goal for a user.

    Args:
        user_id (int): The ID of the user for whom to retrieve the goal.

    Returns:
        Goal | None: The nutritional goal for today, or None if goal with today's date does not exist for the user.
    """
    goal = (
        Goal.query.filter(
            Goal.user_id == user_id,
            Goal.effective_date == date.today(),
        ).first()
    )
    return goal


def get_goal_for_date(user_id: int, selected_date: date) -> Goal | None:
    """Retrieve the most relevant nutritional goal for a user on a given date.

    Finds the latest goal effective on or before the selected date. If none 
    exists, falls back to the earliest available future goal.

    Args:
        user_id (int): The ID of the user for whom to retrieve the goal.
        selected_date (date): The target date for the query.

    Returns:
        Goal | None: The most relevant Goal object, or None if the user 
                     has no goals recorded at all.
    """
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

    return goal

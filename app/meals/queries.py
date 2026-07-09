"""Query functions for retrieving meal data from the database."""

from datetime import date as date_type
from app.models import Meal
from app.db import db


def get_meals_for_date(user_id: int, selected_date: date_type) -> list[Meal]:
    """Retrieve meals for a specific user on a given date.

    Args:
        user_id (int): The ID of the user for whom to retrieve meals.
        selected_date (date_type): The date for which to retrieve meals.

    Returns:
        list[Meal]: A list of meals logged by the user on the specified date.
    """
    return (
        Meal.query
        .filter(Meal.user_id == user_id, Meal.logged_date == selected_date)
        .order_by(Meal.created_at.asc())
        .all()
    )

from datetime import date as date_type
from app.models import Meal
from app.db import db


def get_meals_for_date(user_id: int, selected_date: date_type) -> list[Meal]:
    return (
        Meal.query
        .filter(Meal.user_id == user_id, Meal.logged_date == selected_date)
        .order_by(Meal.created_at.asc())
        .all()
    )

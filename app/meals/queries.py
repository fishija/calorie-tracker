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


def compute_totals(meals: list[Meal]) -> dict:
    return {
        'calories': sum(e.calorie_kcal for e in meals),
        'proteins': sum(e.protein_g for e in meals),
        'carbs': sum(e.carb_g for e in meals),
        'fats': sum(e.fat_g for e in meals),
    }

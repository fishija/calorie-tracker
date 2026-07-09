"""Service functions for meal-related operations."""

from app.models import Meal


def compute_totals(meals: list[Meal]) -> dict:
    """Compute the total nutritional values (calories, proteins, carbs, fats) for a list of meals.

    Args:
        meals (list[Meal]): The list of meal objects to compute totals for.

    Returns:
        dict: A dictionary containing the total nutritional values with keys
            'calories', 'proteins', 'carbs', and 'fats'.
    """
    return {
        "calories": sum(e.calorie_kcal for e in meals),
        "proteins": sum(e.protein_g for e in meals),
        "carbs": sum(e.carb_g for e in meals),
        "fats": sum(e.fat_g for e in meals),
    }

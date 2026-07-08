from app.models import Meal


def compute_totals(meals: list[Meal]) -> dict:
    return {
        'calories': sum(e.calorie_kcal for e in meals),
        'proteins': sum(e.protein_g for e in meals),
        'carbs': sum(e.carb_g for e in meals),
        'fats': sum(e.fat_g for e in meals),
    }

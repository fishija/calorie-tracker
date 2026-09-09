from pydantic import BaseModel


class MealEstimation(BaseModel):
    meal_summary: str
    calorie_kcal: float
    protein_g: float
    fat_g: float
    carb_g: float
    confidence: str
    assumptions: str
    source_type: str

"""JSON schema enforced via tool use, so the response is always structured."""

NUTRITION_TOOL = {
    "name": "log_nutrition",
    "description": "Record the estimated nutritional content of a meal.",
    "input_schema": {
        "type": "object",
        "properties": {
            "meal_summary": {
                "type": "string",
                "description": "Short summary of what was identified.",
            },
            "calorie_kcal": {"type": "number"},
            "protein_g": {"type": "number"},
            "fat_g": {"type": "number"},
            "carb_g": {"type": "number"},
            "confidence": {
                "type": "string",
                "enum": ["low", "medium", "high"],
                "description": "high = clear quantities stated; low = mostly guessed",
            },
            "assumptions": {
                "type": "string",
                "description": "Any portion sizes or ingredients you had to assume",
            },
            "source_type": {
                "type": "string",
                "enum": [
                    "nutrition_label",
                    "packaged_meal_photo",
                    "general_food_photo",
                    "text_description",
                ],
                "description": "Which input was primarily used to produce this estimate",
            },
        },
        "required": [
            "meal_summary",
            "calorie_kcal",
            "protein_g",
            "fat_g",
            "carb_g",
            "confidence",
            "assumptions",
            "source_type",
        ],
    },
}

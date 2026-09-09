"""Estimation functions for meal nutritional content."""

from flask import current_app

from app.llm.prompts import ESTIMATE_MEAL_SYSTEM_PROMPT
from app.llm.schemas import MealEstimation


def estimate_meal(
    description: str, image_bytes_list: list[bytes] | None = None, client=None
) -> MealEstimation:
    """
    Estimate kcal/macros for a meal.

    Args:
        description (str): Text description of the meal (required, primary signal).
        image_bytes_list (list[bytes] | None): Optional list of image bytes (jpg/png).

    Returns:
        dict: A structured dictionary containing the estimated nutritional content,
        confidence level, assumptions made, and the primary source type used
        for the estimate.
    """
    client = client or current_app.extensions["anthropic_client"]
    model = current_app.config["CLAUDE_MODEL"]

    content = []

    if image_bytes_list:
        for img_data in image_bytes_list:
            media_type = "image/jpeg"  # default to jpeg, could be improved to detect type
            content.append(
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": media_type,
                        "data": img_data,
                    },
                }
            )

    prompt = ESTIMATE_MEAL_SYSTEM_PROMPT.format(description=description)

    response = client.messages.parse(
        model=model,
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
        output_format=MealEstimation,
    )

    return response.parsed_output

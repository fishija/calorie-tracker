"""Estimation functions for meal nutritional content."""

from flask import current_app

from app.llm.prompts import ESTIMATE_MEAL_SYSTEM_PROMPT
from app.llm.tools import NUTRITION_TOOL


def estimate_meal(
    description: str, image_bytes_list: list[bytes] | None = None, client=None
) -> dict:
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

    content.append({"type": "text", "text": f"Meal description: {description}"})

    response = client.messages.create(
        model=model,
        max_tokens=500,
        system=ESTIMATE_MEAL_SYSTEM_PROMPT,
        tools=[NUTRITION_TOOL],
        tool_choice={"type": "tool", "name": "log_nutrition"},  # force structured output
        messages=[{"role": "user", "content": content}],
    )

    # Extract the tool call input
    for block in response.content:
        if block.type == "tool_use" and block.name == "log_nutrition":
            return block.input

    raise RuntimeError("Model did not return a tool call — unexpected response format")

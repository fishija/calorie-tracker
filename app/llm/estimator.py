"""Estimation functions for meal nutritional content."""

import anthropic
from flask import current_app
from google import genai

from app.llm.prompts import ESTIMATE_MEAL_SYSTEM_PROMPT
from app.llm.schemas import MealEstimation
from config import LLMProvider, ModelConfig


def _estimate_gemini(
    client, model_name: str, prompt: str, image_bytes_list: list[bytes]
) -> MealEstimation:
    input = [
        {"type": "text", "text": prompt},
    ]

    if image_bytes_list:
        for img_data in image_bytes_list:
            mime_type = "image/jpeg"
            input.append(
                {
                    "type": "image",
                    "mime_type": mime_type,
                    "data": img_data,
                }
            )

    interaction = client.interactions.create(
        model=model_name,
        input=input,
        response_format={
            "type": "text",
            "mime_type": "application/json",
            "schema": MealEstimation.model_json_schema(),
        },
    )
    return MealEstimation.model_validate_json(interaction.output_text)


def _estimate_claude(
    client, model_name: str, prompt: str, image_bytes_list: list[bytes]
) -> MealEstimation:
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

    response = client.messages.parse(
        model=model_name,
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
        output_format=MealEstimation,
    )
    return response.parsed_output


def estimate_meal(description: str, image_bytes_list: list[bytes] | None = None) -> MealEstimation:
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
    model_config: ModelConfig = current_app.config["MODEL_CFG"]

    provider: LLMProvider = model_config.provider
    api_key: str = model_config.api_key
    model_name: str = model_config.model_name

    if provider == LLMProvider.GOOGLE:
        client = genai.Client(api_key=api_key)
        estimate_fn = _estimate_gemini

    elif provider == LLMProvider.ANTHROPIC:
        client = anthropic.Anthropic(api_key=api_key)
        estimate_fn = _estimate_claude

    else:
        raise ValueError(f"Estimation with LLM provider {provider} is not available.")

    prompt = ESTIMATE_MEAL_SYSTEM_PROMPT.format(description=description)

    meal_estimation_object = estimate_fn(client, model_name, prompt, image_bytes_list)
    return meal_estimation_object

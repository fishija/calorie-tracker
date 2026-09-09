from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from app.llm.estimator import estimate_meal
from app.llm.schemas import MealEstimation


@pytest.fixture
def mock_anthropic_client(app):
    """Replace the real Anthropic client with a mock for the duration of a test."""
    mock_client = MagicMock()
    app.extensions["anthropic_client"] = mock_client
    return mock_client


def _fake_parse_response(parsed_output):
    """Build a fake structured Anthropic response."""
    return SimpleNamespace(parsed_output=parsed_output)


class TestEstimateMeal:
    def test_estimate_meal_text_only_returns_parsed_object(self, app, mock_anthropic_client):
        expected = MealEstimation(
            meal_summary="grilled chicken with rice",
            calorie_kcal=450,
            protein_g=40,
            fat_g=10,
            carb_g=45,
            confidence="high",
            assumptions="",
            source_type="text_description",
        )
        mock_anthropic_client.messages.parse.return_value = _fake_parse_response(expected)

        with app.app_context():
            result = estimate_meal("200g grilled chicken, 1 cup rice")

        assert result == expected

    def test_estimate_meal_sends_correct_model_and_forces_tool_choice(
        self, app, mock_anthropic_client
    ):
        mock_anthropic_client.messages.parse.return_value = _fake_parse_response(
            MealEstimation(
                meal_summary="banana",
                calorie_kcal=100,
                protein_g=1,
                fat_g=0,
                carb_g=27,
                confidence="high",
                assumptions="",
                source_type="text_description",
            )
        )

        with app.app_context():
            estimate_meal("a banana")

        _, kwargs = mock_anthropic_client.messages.parse.call_args
        assert kwargs["model"] == app.config["CLAUDE_MODEL"]
        assert kwargs["output_format"] is MealEstimation

    def test_estimate_meal_includes_images_when_provided(self, app, mock_anthropic_client):
        mock_anthropic_client.messages.parse.return_value = _fake_parse_response(
            MealEstimation(
                meal_summary="sandwich",
                calorie_kcal=400,
                protein_g=20,
                fat_g=15,
                carb_g=45,
                confidence="medium",
                assumptions="",
                source_type="image",
            )
        )
        fake_image_bytes = b"fake-jpeg-bytes"

        with app.app_context():
            estimate_meal("a sandwich", image_bytes_list=[fake_image_bytes])

        _, kwargs = mock_anthropic_client.messages.parse.call_args
        assert kwargs["messages"][0]["content"] == kwargs["messages"][0]["content"]

    def test_estimate_meal_returns_parsed_response(self, app, mock_anthropic_client):
        expected = MealEstimation(
            meal_summary="something vague",
            calorie_kcal=0,
            protein_g=0,
            fat_g=0,
            carb_g=0,
            confidence="low",
            assumptions="Insufficient information",
            source_type="text_description",
        )
        mock_anthropic_client.messages.parse.return_value = _fake_parse_response(expected)

        with app.app_context():
            result = estimate_meal("something vague")

        assert result is expected

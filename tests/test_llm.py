from unittest.mock import MagicMock

import pytest

from config import LLMProvider, ModelConfig
from app.llm.estimator import estimate_meal
from app.llm.schemas import MealEstimation


@pytest.fixture
def test_model_config(app):
    model_config = ModelConfig(
        provider=LLMProvider.GOOGLE,
        api_key="test-api-key",
        model_name="test-model",
    )
    app.config["MODEL_CFG"] = model_config
    return model_config


@pytest.fixture
def mock_google_client(monkeypatch, test_model_config):
    """Replace the configured Google client with a mock."""
    mock_client = MagicMock()
    monkeypatch.setattr("app.llm.estimator.genai.Client", MagicMock(return_value=mock_client))
    return mock_client


def _fake_interaction(parsed_output):
    """Build a fake structured Google response."""
    return MagicMock(output_text=parsed_output.model_dump_json())


class TestEstimateMeal:
    def test_estimate_meal_text_only_returns_parsed_object(self, app, mock_google_client):
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
        mock_google_client.interactions.create.return_value = _fake_interaction(expected)

        with app.app_context():
            result = estimate_meal("200g grilled chicken, 1 cup rice")

        assert result == expected

    def test_estimate_meal_sends_correct_model_and_response_schema(
        self, app, mock_google_client, test_model_config
    ):
        expected = MealEstimation(
            meal_summary="banana",
            calorie_kcal=100,
            protein_g=1,
            fat_g=0,
            carb_g=27,
            confidence="high",
            assumptions="",
            source_type="text_description",
        )
        mock_google_client.interactions.create.return_value = _fake_interaction(expected)

        with app.app_context():
            estimate_meal("a banana")

        _, kwargs = mock_google_client.interactions.create.call_args
        assert kwargs["model"] == test_model_config.model_name
        assert kwargs["response_format"]["schema"] == MealEstimation.model_json_schema()

    def test_estimate_meal_includes_images_when_provided(self, app, mock_google_client):
        expected = MealEstimation(
            meal_summary="sandwich",
            calorie_kcal=400,
            protein_g=20,
            fat_g=15,
            carb_g=45,
            confidence="medium",
            assumptions="",
            source_type="image",
        )
        mock_google_client.interactions.create.return_value = _fake_interaction(expected)
        fake_image_bytes = b"fake-jpeg-bytes"

        with app.app_context():
            estimate_meal("a sandwich", image_bytes_list=[fake_image_bytes])

        _, kwargs = mock_google_client.interactions.create.call_args
        assert kwargs["input"][0]["type"] == "text"
        assert kwargs["input"][1]["type"] == "image"
        assert kwargs["input"][1]["data"] == fake_image_bytes

    def test_estimate_meal_returns_parsed_response(self, app, mock_google_client):
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
        mock_google_client.interactions.create.return_value = _fake_interaction(expected)

        with app.app_context():
            result = estimate_meal("something vague")

        assert result == expected

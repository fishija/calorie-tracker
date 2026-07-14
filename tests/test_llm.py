from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from app.llm.estimator import estimate_meal


@pytest.fixture
def mock_anthropic_client(app):
    """Replace the real Anthropic client with a mock for the duration of a test."""
    mock_client = MagicMock()
    app.extensions["anthropic_client"] = mock_client
    return mock_client


def _fake_tool_response(input_dict):
    """Build a fake anthropic response with one tool_use block."""
    block = SimpleNamespace(type="tool_use", name="log_nutrition", input=input_dict)
    return SimpleNamespace(content=[block])


class TestEstimateMeal:
    def test_estimate_meal_text_only_returns_parsed_dict(self, app, mock_anthropic_client):
        expected = {
            "meal_summary": "grilled chicken with rice",
            "calorie_kcal": 450,
            "protein_g": 40,
            "fat_g": 10,
            "carb_g": 45,
            "confidence": "high",
            "assumptions": "",
            "source_type": "text_description",
        }
        mock_anthropic_client.messages.create.return_value = _fake_tool_response(expected)

        with app.app_context():
            result = estimate_meal("200g grilled chicken, 1 cup rice")

        assert result == expected

    def test_estimate_meal_sends_correct_model_and_forces_tool_choice(
        self, app, mock_anthropic_client
    ):
        mock_anthropic_client.messages.create.return_value = _fake_tool_response({})

        with app.app_context():
            estimate_meal("a banana")

        _, kwargs = mock_anthropic_client.messages.create.call_args
        assert kwargs["model"] == app.config["CLAUDE_MODEL"]
        assert kwargs["tool_choice"] == {"type": "tool", "name": "log_nutrition"}
        assert kwargs["tools"] == [
            __import__("app.llm.tools", fromlist=["NUTRITION_TOOL"]).NUTRITION_TOOL
        ]

    def test_estimate_meal_includes_images_when_provided(self, app, mock_anthropic_client):
        mock_anthropic_client.messages.create.return_value = _fake_tool_response({})
        fake_image_bytes = b"fake-jpeg-bytes"

        with app.app_context():
            estimate_meal("a sandwich", image_bytes_list=[fake_image_bytes])

        _, kwargs = mock_anthropic_client.messages.create.call_args
        sent_content = kwargs["messages"][0]["content"]
        image_blocks = [b for b in sent_content if b["type"] == "image"]
        assert len(image_blocks) == 1
        assert image_blocks[0]["source"]["data"] == fake_image_bytes

    def test_estimate_meal_raises_if_no_tool_call_returned(self, app, mock_anthropic_client):
        text_block = SimpleNamespace(type="text", text="I'm not sure")
        mock_anthropic_client.messages.create.return_value = SimpleNamespace(content=[text_block])

        with app.app_context():
            with pytest.raises(RuntimeError, match="did not return a tool call"):
                estimate_meal("something vague")

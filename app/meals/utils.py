"""Utility functions for meal-related operations."""

import uuid

from werkzeug.utils import secure_filename


def make_unique_filename(original_filename: str) -> str:
    """Generate a unique filename for an uploaded file, preserving its extension.

    Args:
        original_filename (str): The original name of the uploaded file.

    Returns:
        str: A unique filename with the same extension as the original file.
    """
    safe_name = secure_filename(original_filename)
    ext = safe_name.rsplit(".", 1)[-1].lower() if "." in safe_name else ""
    unique_id = uuid.uuid4().hex
    return f"{unique_id}.{ext}" if ext else unique_id

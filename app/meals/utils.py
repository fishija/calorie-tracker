"""Utility functions for meal-related operations."""

import base64
import os
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


def uploaded_files_to_bytes(uploaded_files) -> list[bytes]:
    """Convert a list of uploaded files to a list of bytes.

    Args:
        uploaded_files (list): A list of uploaded file objects.

    Returns:
        list[bytes]: A list of byte representations of the uploaded files.
    """
    return [
        base64.standard_b64encode(file.stream.read()).decode("utf-8") for file in uploaded_files
    ]


def stored_files_to_bytes(upload_folder: str, filenames: list[str]) -> list[bytes]:
    """Convert stored upload files to a list of base64-encoded bytes.

    Args:
        upload_folder (str): The directory where uploaded files are stored.
        filenames (list[str]): The filenames of the stored files.

    Returns:
        list[bytes]: A list of byte representations of the stored files.
        Files that no longer exist on disk are skipped.
    """
    encoded = []
    for filename in filenames:
        file_path = os.path.join(upload_folder, filename)
        if not os.path.exists(file_path):
            continue
        with open(file_path, "rb") as f:
            encoded.append(base64.standard_b64encode(f.read()).decode("utf-8"))
    return encoded

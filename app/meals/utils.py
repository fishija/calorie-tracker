import uuid
from werkzeug.utils import secure_filename


def make_unique_filename(original_filename: str) -> str:
    safe_name = secure_filename(original_filename)
    ext = safe_name.rsplit(".", 1)[-1].lower() if "." in safe_name else ""
    unique_id = uuid.uuid4().hex
    return f"{unique_id}.{ext}" if ext else unique_id

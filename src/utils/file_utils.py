import os
import uuid
from pathlib import Path

def save_image(image_bytes: bytes, filename: str, status_folder: str) -> str:
    """
    Saves the image to a specified subfolder (e.g., 'success', 'failed')
    within the main static outputs directory.
    """

    base_dir = Path(__file__).resolve().parent.parent

    output_dir = base_dir / "static" / "outputs" / status_folder
    output_dir.mkdir(parents=True, exist_ok=True)

    output_filename = f"{uuid.uuid4().hex}_{filename}"
    output_path = output_dir / output_filename

    with open(output_path, "wb") as f:
        f.write(image_bytes)


    return str(output_path)
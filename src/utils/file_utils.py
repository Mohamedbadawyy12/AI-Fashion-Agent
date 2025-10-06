import os
import uuid
from pathlib import Path

def save_temp_image(image_bytes: bytes, filename: str) -> str:
    # استخدم المسار الصحيح لمجلد المشروع
    base_dir = Path(__file__).resolve().parent.parent  # يرجع لـ src/
    output_dir = base_dir / "static" / "outputs"
    output_dir.mkdir(parents=True, exist_ok=True)

    output_filename = f"{uuid.uuid4().hex}_{filename}"
    output_path = output_dir / output_filename

    with open(output_path, "wb") as f:
        f.write(image_bytes)

    # ارجّع المسار الكامل
    return str(output_path)

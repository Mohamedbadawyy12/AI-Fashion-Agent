import os, uuid

def save_temp_image(image_bytes: bytes, filename: str) -> str:
    os.makedirs("/tmp/outputs", exist_ok=True)
    output_path = f"/tmp/outputs/{uuid.uuid4().hex}_{filename}"
    with open(output_path, "wb") as f:
        f.write(image_bytes)
    return output_path

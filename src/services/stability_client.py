import requests
import base64
from io import BytesIO
from PIL import Image
from core.config import settings
import logging

logging.basicConfig(level=logging.INFO)

def resize_image_to_allowed_dimensions(image_bytes: bytes, target_size=(1024, 1024)) -> bytes:
    """Resize any uploaded image to allowed dimensions."""
    image = Image.open(BytesIO(image_bytes)).convert("RGB")
    image = image.resize(target_size, Image.LANCZOS)
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def generate_image_from_prompt(prompt: str, init_image: bytes = None) -> bytes:
    api_host = "https://api.stability.ai"
    engine_id = "stable-diffusion-xl-1024-v1-0"
    api_key = settings.STABILITY_API_KEY

    if not api_key:
        raise ValueError("Missing STABILITY_API_KEY in environment")

    # ---- TEXT → IMAGE ----
    if init_image is None:
        logging.info("🎨 Mode: TEXT-to-IMAGE — No initial image provided.")
        response = requests.post(
            f"{api_host}/v1/generation/{engine_id}/text-to-image",
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Authorization": f"Bearer {api_key}",
            },
            json={
                "text_prompts": [{"text": prompt}],
                "cfg_scale": 7,
                "height": 1024,
                "width": 1024,
                "samples": 1,
                "steps": 30,
            },
            timeout=60,
        )

    # ---- IMAGE → IMAGE ----
    else:
        logging.info("🎨 Mode: IMAGE-to-IMAGE — Initial image detected and used.")

        # ✅ Resize uploaded image to allowed size
        resized_image = resize_image_to_allowed_dimensions(init_image, target_size=(1024, 1024))

        response = requests.post(
            f"{api_host}/v1/generation/{engine_id}/image-to-image",
            headers={
                "Accept": "application/json",
                "Authorization": f"Bearer {api_key}",
            },
            files={
                "init_image": ("image.png", resized_image, "image/png"),
            },
            data={
                "text_prompts[0][text]": prompt,
                "image_strength": 0.65,
                "cfg_scale": 7,
                "samples": 1,
                "steps": 30,
            },
            timeout=60,
        )

    if response.status_code != 200:
        logging.error(f"❌ Stability API error: {response.status_code} {response.text}")
        raise Exception(f"Stability API error: {response.status_code} {response.text}")

    data = response.json()
    b64 = data["artifacts"][0]["base64"]
    logging.info("✅ Image generation successful.")
    return base64.b64decode(b64)

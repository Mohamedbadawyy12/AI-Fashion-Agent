import os
import time
import mimetypes
from io import BytesIO
from google import genai
from google.genai import types
from core.config import settings
import logging

logging.basicConfig(level=logging.INFO)

MODEL_NAME = "gemini-2.5-flash-image-preview"


def generate_image_from_prompt(prompt: str, init_image: bytes = None) -> bytes:
    """
    Generates an image using Google Gemini.
    If init_image is provided, it performs IMAGE-to-IMAGE.
    Otherwise, it performs TEXT-to-IMAGE.
    """
    api_key = os.environ.get("GOOGLE_API_KEY") or settings.GOOGLE_API_KEY
    if not api_key:
        raise ValueError("Missing GEMINI_API_KEY in environment or settings")

    client = genai.Client(api_key=api_key)

    contents = []
    if init_image:
        logging.info("🎨 Mode: IMAGE-to-IMAGE — Using product base image.")
        mime_type = "image/png"
        contents.append(
            types.Part(inline_data=types.Blob(data=init_image, mime_type=mime_type))
        )
    else:
        logging.info("🎨 Mode: TEXT-to-IMAGE — Generating from text prompt only.")

    contents.append(genai.types.Part.from_text(text=prompt))

    generate_content_config = types.GenerateContentConfig(
        response_modalities=["IMAGE", "TEXT"]
    )

    stream = client.models.generate_content_stream(
        model=MODEL_NAME,
        contents=contents,
        config=generate_content_config,
    )

    # process streamed output (Gemini sends chunks)
    output_image = None
    for chunk in stream:
        if (
            not chunk.candidates
            or not chunk.candidates[0].content
            or not chunk.candidates[0].content.parts
        ):
            continue

        for part in chunk.candidates[0].content.parts:
            if part.inline_data and part.inline_data.data:
                output_image = part.inline_data.data
                logging.info("✅ Gemini image generation complete.")
                break

    if not output_image:
        raise RuntimeError("No image data returned from Gemini API")

    return output_image

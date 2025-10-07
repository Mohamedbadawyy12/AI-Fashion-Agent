import logging
from io import BytesIO
from core.config import settings
from google import genai
from google.genai import types
from PIL import Image
import json
import base64

logging.basicConfig(level=logging.INFO)

def _call_gemini_api(prompt_parts: list, config: types.GenerateContentConfig = None) -> genai.types.GenerateContentResponse:
    """
    A unified helper function to call the Gemini API using the correct client initialization
    and the most capable model for the job.
    """
    api_key = settings.GOOGLE_API_KEY
    if not api_key:
        raise ValueError("Missing GOOGLE_API_KEY")
    
    client = genai.Client(api_key=api_key)
    # We will consistently use the most advanced image model available
    model = client.get_model("models/gemini-2.5-flash-image-preview")
    
    return model.generate_content(contents=prompt_parts, generation_config=config)

def get_segmentation_mask(image_bytes: bytes) -> bytes:
    """
    Uses Gemini's native segmentation feature to get a precise mask of text/logos.
    """
    logging.info("🎭 Generating segmentation mask using native API...")

    im = Image.open(BytesIO(image_bytes))

    prompt = """
    Give the segmentation masks for all visible text and logos on the product.
    Output a JSON list where each element has:
      - "box_2d": [y0, x0, y1, x1] (bounding box normalized to 1000 scale)
      - "mask": "data:image/png;base64,..." (the segmentation mask)
    """

    config = types.GenerateContentConfig(
        response_mime_type="application/json",
        thinking_config=types.ThinkingConfig(thinking_budget=0)
    )

    response = _call_gemini_api([prompt, im], config)

    try:
        items = json.loads(response.text)
    except (json.JSONDecodeError, AttributeError) as e:
        raise RuntimeError(f"Invalid or empty JSON response from Gemini: {e}. Response text: {getattr(response, 'text', 'N/A')}")

    if not items:
        raise RuntimeError("Segmentation failed: No items were detected in the JSON response.")

    final_mask = Image.new("L", im.size, 0) # 'L' mode for grayscale (black and white)

    for item in items:
        box = item.get("box_2d")
        png_str = item.get("mask")

        if not box or not png_str:
            logging.warning("Skipping an item in segmentation response due to missing 'box_2d' or 'mask'.")
            continue

        y0, x0, y1, x1 = [int(c / 1000 * dim) for c, dim in zip(box, [im.size[1], im.size[0], im.size[1], im.size[0]])]

        if y0 >= y1 or x0 >= x1: continue

        png_str = png_str.removeprefix("data:image/png;base64,")
        
        # Safety check for base64 padding
        missing_padding = len(png_str) % 4
        if missing_padding:
            png_str += "=" * (4 - missing_padding)

        try:
            mask_data = base64.b64decode(png_str)
            mask_part = Image.open(BytesIO(mask_data)).resize((x1 - x0, y1 - y0), Image.Resampling.BILINEAR)
            final_mask.paste(mask_part, (x0, y0))
        except Exception as e:
            logging.error(f"Could not process a mask part due to an error: {e}. Skipping this part.")
            continue

    buffer = BytesIO()
    final_mask.save(buffer, format="PNG")
    logging.info("✅ Native segmentation mask generated successfully.")
    return buffer.getvalue()


def inpaint_with_mask_and_reference(
    generated_image_bytes: bytes,
    mask_bytes: bytes,
    original_product_bytes: bytes
) -> bytes:
    """
    Performs a precise, mask-guided visual transfer from a reference image.
    """
    logging.info("🎨 Performing final mask-guided visual transfer...")
    
    prompt = [
        "You are an expert digital image restorer.",
        "Your task is to perform a precise visual transfer using three images: the 'generated image', the 'mask', and the 'original product image'.",
        "You must ONLY modify the pixels in the 'generated image' that correspond to the white areas of the 'mask'.",
        "For those areas, you must look at the 'original product image' and perfectly replicate the appearance of its text and logo.",
        "All pixels in the black areas of the 'mask' must remain absolutely unchanged.",
        "This is the generated image (the one to be corrected):",
        types.Part(inline_data=types.Blob(data=generated_image_bytes, mime_type='image/jpeg')),
        "This is the mask (defines the work area):",
        types.Part(inline_data=types.Blob(data=mask_bytes, mime_type='image/png')),
        "This is the original product image (the source of truth):",
        types.Part(inline_data=types.Blob(data=original_product_bytes, mime_type='image/jpeg')),
    ]

    config = types.GenerationConfig(response_modalities=["IMAGE"])
    response = _call_gemini_api(prompt, config)

    for part in response.candidates[0].content.parts:
        if part.inline_data:
            logging.info("✅ Final visual transfer completed successfully.")
            return part.inline_data.data
            
    raise RuntimeError("No image data returned from in-painting API call.")
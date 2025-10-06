import logging
from services.gemini_image_gen import generate_image_from_prompt

logging.basicConfig(level=logging.INFO)

def generate_node(state):
    """Generate an image from the enhanced prompt.
    - If a product_image exists → use image-to-image mode.
    - Otherwise → text-to-image mode.
    """
    try:
        if state.product_image:
            logging.info("🧠 Mode: IMAGE-to-IMAGE — Using uploaded product image as base.")
            generated = generate_image_from_prompt(
                prompt=state.enhanced_prompt,
                init_image=state.product_image
            )
        else:
            logging.info("🧠 Mode: TEXT-to-IMAGE — No initial image provided.")
            generated = generate_image_from_prompt(
                prompt=state.enhanced_prompt
            )

        state.generated_image = generated
        logging.info("✅ Image generation successful.")
        return state

    except Exception as e:
        logging.error(f"❌ Image generation failed: {e}")
        raise

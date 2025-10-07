import logging
from services.gemini_mask_based_editor import (
    get_segmentation_mask,
    inpaint_with_mask_and_reference
)

logging.basicConfig(level=logging.INFO)

def text_correction_node(state):
    """
    Orchestrates the definitive, two-step visual text correction process:
    1. Generates a precise segmentation mask using Gemini's native feature.
    2. Performs a mask-guided visual transfer from the original product image.
    """
    if not state.product_image or not state.generated_image:
        logging.warning("⏩ Text Correction Node: Missing images. Skipping.")
        return state

    try:
        logging.info("🛠️ Text Correction Node: Starting definitive, segmentation-based correction...")

        # Step 1: Generate a segmentation mask from the generated image.
        mask_bytes = get_segmentation_mask(state.generated_image)

        # Step 2: Perform the precise, mask-guided visual transfer.
        corrected_image_bytes = inpaint_with_mask_and_reference(
            generated_image_bytes=state.generated_image,
            mask_bytes=mask_bytes,
            original_product_bytes=state.product_image
        )

        state.generated_image = corrected_image_bytes
        logging.info("✅ Text Correction Node: Image successfully updated via segmentation.")
        state.text_correction_applied = True

    except Exception as e:
        logging.error(f"❌ Text Correction Node failed: {e}")
        state.text_correction_applied = True

    return state
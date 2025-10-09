import logging
from services.gemini_quality_assessor import assess_image_quality
from utils.file_utils import save_image

logging.basicConfig(level=logging.INFO)

def quality_node(state):
    """
    Assesses the image quality. If accepted, it saves the image to the 'success' folder.
    """
    logging.info("🧐 Quality Node: Assessing generated image...")
    assessment = assess_image_quality(state)
    
    # Store the simple assessment in the state
    state.quality_assessment = assessment

    if assessment.get("decision") == "accept":
        logging.info("✅ Image passed quality check. Saving to 'success' folder.")
        path = save_image(state.generated_image, state.filename, "success")
        state.output_path = path
    else:
        logging.warning(f"❌ Image failed quality check. Reason: {assessment.get('reason')}")
        state.output_path = None

    return state
import logging
from services.gemini_quality_assessor import assess_image_quality
from utils.file_utils import save_image

logging.basicConfig(level=logging.INFO)

def quality_node(state):
    """
    Assesses the image quality based on the detailed assessment service.
    If BOTH image and text are accepted, it saves the image to the 'success' folder.
    Otherwise, it prepares for the next step (correction or retry).
    """
    logging.info("🧐 Quality Node: Assessing generated image...")
    assessment = assess_image_quality(state)
    
    # Store the detailed assessment in the state for the 'brain' to use
    state.quality_assessment = assessment

    # --- THIS IS THE CORRECTED LOGIC ---
    # Check for the golden path: everything is perfect.
    if assessment.get("image_decision") == "accept" and assessment.get("text_decision") == "accept":
        logging.info("✅ Image and Text passed quality check. Saving to 'success' folder.")
        path = save_image(state.generated_image, state.filename, "success")
        state.output_path = path
    else:
        # If anything is not perfect, we log it as a warning and let the 'brain' decide what to do.
        # We do NOT save the image here, as it's not the final successful output.
        logging.warning(f"-QA Notice- Image Decision: {assessment.get('image_decision')}, Text Decision: {assessment.get('text_decision')}. Reason: {assessment.get('reason')}")
        state.output_path = None
    # ------------------------------------

    return state
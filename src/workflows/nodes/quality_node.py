import logging
from services.gemini_quality_assessor import assess_image_quality
from utils.file_utils import save_image # <--  1. تعديل الـ import

logging.basicConfig(level=logging.INFO)

def quality_node(state):
    """
    Assesses the image quality. If accepted, it saves the image to the 'success' folder.
    """
    logging.info("🧐 Quality Node: Assessing generated image...")
    assessment = assess_image_quality(state)
    
    state.quality_assessment = assessment

    if assessment.get("decision") == "accept":
        logging.info("✅ Image passed quality check.")
        # 2. الحفظ في مجلد 'success'
        path = save_image(state.generated_image, state.filename, "success")
        state.output_path = path
    else:
        logging.warning("❌ Image failed quality check. Reason: " + assessment.get("reason", "No reason provided."))
        state.output_path = None

    return state
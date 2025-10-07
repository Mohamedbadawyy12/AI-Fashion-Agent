import base64
import logging
import json
from io import BytesIO
from PIL import Image
import google.generativeai as genai
from core.config import settings

logging.basicConfig(level=logging.INFO)

def image_bytes_to_base64(image_bytes: bytes) -> str:
    """Helper function to convert image bytes to a base64 encoded string."""
    return base64.b64encode(image_bytes).decode('utf-8')

def assess_image_quality(state) -> dict:
    """
    Analyzes the generated image against the prompt and original product image.
    Returns a dictionary with a 'decision' ('accept' or 'reject') and a 'reason'.
    """
    try:
        logging.info("🧐 Kicking off Quality Assessor Service...")
        
        genai.configure(api_key=settings.GOOGLE_API_KEY)
        # 1. استخدام نفس النموذج الذي يعمل في توليد الصور لضمان التوافق
        model = genai.GenerativeModel('gemini-2.5-flash-image-preview')

        system_prompt = f"""
        You are a meticulous Quality Assurance Art Director at a high-end fashion agency.
        Your task is to critically evaluate a newly generated AI image based on two criteria: the creative brief and the original product.

        **1. Creative Brief (The Prompt):**
        "{state.enhanced_prompt}"

        **2. The Task:**
        Look at the "Generated Image" and compare it to the "Original Product Image" and the "Creative Brief".
        - Does the generated image follow the creative brief's mood, setting, and description?
        - Is the product from the original image represented ACCURATELY in the generated image? (Check for colors, shapes, and especially text/logos).
        - Are there any obvious AI flaws like distorted faces, hands with extra fingers, or unnatural textures?

        **3. Your Decision:**
        Based on your analysis, respond with ONLY a JSON object in the following format:
        - If the image is excellent and ready for the client, use:
          {{"decision": "accept", "reason": "A brief explanation of why it's good."}}
        - If the image has flaws and needs to be regenerated, use:
          {{"decision": "reject", "reason": "A brief, constructive critique of what went wrong, which will be used to improve the next attempt."}}
        
        Your entire response must be a single, valid JSON object and nothing else.
        """
        
        original_product_img = Image.open(BytesIO(state.product_image)) if state.product_image else None
        generated_img = Image.open(BytesIO(state.generated_image))
        
        contents = [system_prompt, "Original Product Image:", original_product_img, "Generated Image:", generated_img]
        contents = [part for part in contents if part is not None]

        response = model.generate_content(contents)
        json_response_text = response.text.strip().replace("```json", "").replace("```", "")
        assessment = json.loads(json_response_text)
        
        logging.info(f"✅ Quality Assessment Complete: Decision is '{assessment.get('decision')}' because '{assessment.get('reason')}'")
        return assessment

    except Exception as e:
        logging.error(f"❌ Quality Assessor Service failed: {e}")
        return {"decision": "accept", "reason": "QA service failed, accepting by default."}
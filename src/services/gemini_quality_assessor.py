import logging
import json
import base64 # <-- 1. Add base64 import
from core.config import settings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage

logging.basicConfig(level=logging.INFO)

# 2. Define the helper function directly in this file
def image_bytes_to_base64(image_bytes: bytes) -> str:
    """Helper function to convert image bytes to a base64 encoded string."""
    return base64.b64encode(image_bytes).decode('utf-8')


def assess_image_quality(state) -> dict:
    """
    Analyzes the generated image against the prompt and returns a simple
    'accept' or 'reject' decision.
    """
    try:
        logging.info("🧐 Kicking off Simplified Quality Assessor Service...")

        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash-image-preview",
            google_api_key=settings.GOOGLE_API_KEY,
        )

        system_prompt = f"""
        You are a meticulous Quality Assurance Art Director. Your task is to evaluate a generated AI image.
        Compare the "Generated Image" to the "Creative Brief" and the "Original Product Image".

        **Creative Brief:** "{state.enhanced_prompt}"

        **Evaluation Criteria:**
        1.  **Brief Adherence:** Does the image match the brief's mood, setting, and description?
        2.  **Product Accuracy:** Is the product represented accurately in shape, color, and branding compared to the original?
        3.  **Technical Flaws:** Are there any obvious AI flaws like distorted faces, hands, or textures?

        **Your Decision:**
        Respond with ONLY a JSON object with two keys: "decision" and "reason".
        - If the image is excellent and meets all criteria, use:
          {{"decision": "accept", "reason": "A brief explanation of why it's good."}}
        - If the image has any significant flaws, use:
          {{"decision": "reject", "reason": "A brief, constructive critique of what went wrong."}}
        """

        content_parts = [
            {"type": "text", "text": "Please evaluate the generated image based on my instructions."},
        ]
        
        if state.product_image:
            original_base64 = image_bytes_to_base64(state.product_image)
            content_parts.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{original_base64}"}
            })

        generated_base64 = image_bytes_to_base64(state.generated_image)
        content_parts.append({
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;base64,{generated_base64}"}
        })
        
        message = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=content_parts)
        ]

        response = llm.invoke(message)
        json_response_text = response.content.strip().replace("```json", "").replace("```", "")
        assessment = json.loads(json_response_text)
        
        logging.info(f"✅ Simplified Assessment Complete: Decision is '{assessment.get('decision')}'")
        return assessment

    except Exception as e:
        logging.error(f"❌ Quality Assessor Service failed: {e}")
        return {"decision": "accept", "reason": "QA service failed, accepting by default."}
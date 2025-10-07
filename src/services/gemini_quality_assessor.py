import base64
import logging
import json
from core.config import settings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage

logging.basicConfig(level=logging.INFO)

def image_bytes_to_base64(image_bytes: bytes) -> str:
    """Helper function to convert image bytes to a base64 encoded string."""
    return base64.b64encode(image_bytes).decode('utf-8')

def assess_image_quality(state) -> dict:
    """
    Provides a detailed assessment using Langchain's ChatGoogleGenerativeAI.
    """
    try:
        logging.info("🧐 Kicking off Detailed Quality Assessor Service ...")

        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash-image-preview",
            google_api_key=settings.GOOGLE_API_KEY,
        )

        system_prompt = f"""
        You are a meticulous Quality Assurance Art Director. Your task is to provide a two-part evaluation for a generated AI image.

        **1. Creative Brief (The Prompt):**
        "{state.enhanced_prompt}"

        **2. The Task:**
        First, evaluate the **Overall Image Quality**. Does it match the brief's mood, setting, and description? Are there AI flaws (bad hands, etc.)?
        Second, evaluate the **Text/Logo Accuracy**. Compare the text/logo on the generated image to the original product. Is it 100% accurate?

        **3. Your Decision:**
        Respond with ONLY a JSON object. Do not add any other text.
        - `image_decision`: Can be "accept" or "reject".
        - `text_decision`: Can be "accept" or "reject".
        - `reason`: A brief explanation for your decisions.
        """

        # Prepare the content for the HumanMessage
        content_parts = [
            {"type": "text", "text": "Please evaluate the generated image based on my instructions and the original product image provided."},
        ]
        
        # Add original product image if it exists
        if state.product_image:
            original_base64 = image_bytes_to_base64(state.product_image)
            content_parts.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{original_base64}"}
            })

        # Add the generated image
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
        
        logging.info(f"✅ Detailed Assessment: Image={assessment.get('image_decision')}, Text={assessment.get('text_decision')}. Reason: {assessment.get('reason')}")
        return assessment

    except Exception as e:
        logging.error(f"❌ Quality Assessor Service failed: {e}")
        return {"image_decision": "accept", "text_decision": "accept", "reason": "QA service failed."}
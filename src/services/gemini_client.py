import logging
from core.config import settings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

# إعداد اللوج
logging.basicConfig(level=logging.INFO)

def enhance_prompt_with_gemini(base_prompt: str) -> str:
    """Enhance the prompt using Gemini client and log the process."""
    try:
        logging.info("🎨 Starting Gemini prompt enhancement...")
        logging.info(f"📝 Base prompt received: {base_prompt}")

        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-pro",
            google_api_key=settings.GOOGLE_API_KEY,
        )

        structured = f"""
        You are a professional fashion photographer and prompt engineer.
        Expand the user's short description into a single-line, highly-detailed photography prompt
        for a photorealistic image. Respect the subject gender and the clothing described.
        User description: {base_prompt}
        Include: model description, pose, camera, lighting, fabric texture, setting (Egyptian/urban), aesthetic.
        Return the single-line prompt only.
        """

        message = HumanMessage(content=structured)
        response = llm.invoke([message])

        enhanced = response.content.strip()
        logging.info("✅ Gemini prompt enhancement successful.")
        logging.info(f"✨ Enhanced prompt: {enhanced}")

        return enhanced

    except Exception as e:
        logging.warning(f"⚠️ Gemini enhancement failed — fallback used. Error: {e}")

        fallback_prompt = (
            f"Photorealistic, professional fashion photo of an Egyptian model wearing {base_prompt}. "
            "Studio-quality lighting, realistic fabric texture, full body, editorial pose, high-resolution."
        )

        logging.info(f"🪄 Fallback prompt used: {fallback_prompt}")
        return fallback_prompt

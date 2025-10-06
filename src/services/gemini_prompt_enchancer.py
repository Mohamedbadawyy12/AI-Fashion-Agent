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
        You are an expert fashion photographer and a creative director, known for crafting highly detailed prompts for AI image generation.
        Your task is to take a user's simple description and expand it into a rich, detailed, single-paragraph photographic prompt.

        **User's Description:** "{base_prompt}"

        **Instructions:**
        - **Subject & Clothing:** Start by describing the model and the clothing item from the user's description in great detail. Mention fabric textures (e.g., "soft cotton," "glossy silk").
        - **Setting:** Place the model in a specific, atmospheric Egyptian urban setting (e.g., "a historic balcony in Zamalek overlooking the Nile," "a bustling alley in Khan el-Khalili at golden hour," "a modern rooftop cafe in New Cairo at dusk").
        - **Pose:** Describe a natural and elegant pose. (e.g., "leaning gently against a railing," "walking confidently towards the camera," "sitting gracefully on a vintage chair").
        - **Camera & Shot:** Specify the camera shot and lens. (e.g., "Medium full-shot with a 85mm lens," "Close-up portrait with a 50mm f/1.8 lens," "Dynamic wide-angle shot").
        - **Lighting:** Describe the lighting in detail. (e.g., "Warm, cinematic golden hour lighting," "Soft, diffused morning light," "Dramatic, high-contrast studio lighting").
        - **Aesthetic & Mood:** Define the overall mood. (e.g., "Aesthetic: editorial fashion, moody, cinematic, nostalgic").
        - **Final Output:** Combine all these elements into a single, cohesive, and highly descriptive paragraph. Do not return a list or bullet points.
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

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
        You are a world-class creative director at a leading AI modeling agency. Your expertise lies in translating client briefs into rich, detailed, and executable prompts for AI image generation.

        **Client's Brief:** "{base_prompt}"

        **Your Task:**
        Based *only* on the client's brief, expand it into a comprehensive, single-paragraph photographic prompt. Your goal is to select the most fitting elements to create a marketable and high-impact commercial image.

        **Instructions:**
        1.  **Analyze the Brief:** First, understand the product and the core feeling the client wants (e.g., "luxury," "youthful," "rugged," "natural").
        2.  **Select a Setting:** Based on your analysis, choose a compelling setting. Do NOT default to one location type. Consider options like: a minimalist high-tech studio, a vibrant urban street-style scene (e.g., Tokyo, London), a serene natural landscape (e.g., Swiss Alps, coastal beach), a luxurious and opulent interior, or a rustic countryside backdrop. The setting must complement the product.
        3.  **Define the Model:** Describe a model whose ethnicity, style, and expression fit the brand and setting.
        4.  **Clothing & Styling:** Describe the model's attire in detail, ensuring it aligns with the overall aesthetic and doesn't clash with the product.
        5.  **Pose & Interaction:** Detail a natural, confident pose where the model interacts organically with the product. The product must be clearly visible, held naturally, and presented accurately without distortion to its shape, size, or branding.
        6.  **Photography Specs:** Specify the camera shot (e.g., "Medium shot," "Dynamic full-body shot"), lens (e.g., "85mm prime lens," "35mm wide-angle"), and lighting (e.g., "Soft diffused studio light," "Dramatic golden hour sunlight," "High-contrast cinematic lighting").
        7.  **Mood & Aesthetic:** Define the final mood (e.g., "Aesthetic: clean, commercial, sophisticated, energetic, moody").
        8.  **Final Output:** Weave all these elements into one cohesive, highly-descriptive paragraph. Do not use lists or placeholders. The final text must be a ready-to-use prompt.
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

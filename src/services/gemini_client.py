from core.config import settings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage




def enhance_prompt_with_gemini(base_prompt: str) -> str:
    """"enhancing the prompt using gemini client"""
    try:



        llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-pro-latest",
        google_api_key=settings.GOOGLE_API_KEY,
        )


        structured = f"""
        You are a professional fashion photographer and prompt engineer. Expand the user's short description into a single-line, highly-detailed photography prompt for a photorealistic image. Respect the subject gender and the clothing described.
        User description: {base_prompt}
        Include: model description, pose, camera, lighting, fabric texture, setting (Egyptian/urban), aesthetic.
        Return the single-line prompt only.
        """
        message = HumanMessage(content=structured)
        response = llm.invoke([message])
        return response.content.strip()
    except Exception:

        return (
        f"Photorealistic, professional fashion photo of an Egyptian model wearing {base_prompt}. "
        "Studio-quality lighting, realistic fabric texture, full body, editorial pose, high-resolution."
        )
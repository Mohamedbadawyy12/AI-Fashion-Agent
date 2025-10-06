from services.gemini_prompt_enchancer import enhance_prompt_with_gemini

def prompt_node(state):
    enhanced = enhance_prompt_with_gemini(state.description)
    state.enhanced_prompt = enhanced
    return state

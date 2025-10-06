from services.stability_client import generate_image_from_prompt

def generate_node(state):
    generated = generate_image_from_prompt(state.enhanced_prompt)
    state.generated_image = generated
    return state

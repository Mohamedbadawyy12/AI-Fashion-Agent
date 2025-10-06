from services.image_tools import remove_background

def preprocess_node(state):
    cleaned_image = remove_background(state.product_image)
    state.product_image = cleaned_image
    return state

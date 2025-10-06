from utils.file_utils import save_temp_image

def quality_node(state):
    # هنا ممكن تضيف فلتر أو تقييم للصورة
    path = save_temp_image(state.generated_image, state.filename)
    state.output_path = path
    return state

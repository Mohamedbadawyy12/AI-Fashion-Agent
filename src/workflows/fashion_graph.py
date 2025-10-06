from langgraph.graph import StateGraph
from models.state import FashionState
from workflows.nodes.prompt_node import prompt_node
from workflows.nodes.generate_node import generate_node
from workflows.nodes.quality_node import quality_node


def run_workflow(description: str, image_bytes: bytes = None, filename: str = "generated.png") -> str:
    """
    Executes the LangGraph workflow end-to-end.
    - If image_bytes is provided → image-to-image generation
    - Otherwise → text-to-image generation
    """

    graph = StateGraph(FashionState)

    # Define graph flow
    # graph.add_node("preprocess", preprocess_node)
    graph.add_node("prompt", prompt_node)
    graph.add_node("generate", generate_node)
    graph.add_node("quality", quality_node)

    # Set flow order
    graph.add_edge("prompt", "generate")
    graph.add_edge("generate", "quality")

    graph.set_entry_point("prompt")

    chain = graph.compile()

    # Build state object
    state = FashionState(
        description=description,
        product_image=image_bytes,
        filename=filename,
        mode="image-to-image" if image_bytes else "text-to-image"
    )

    # Run workflow
    final_state = chain.invoke(state)

    return final_state.get("output_path")

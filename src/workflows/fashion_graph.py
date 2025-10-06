from langgraph.graph import StateGraph
from models.state import FashionState
from workflows.nodes.preprocess_node import preprocess_node
from workflows.nodes.prompt_node import prompt_node
from workflows.nodes.generate_node import generate_node
from workflows.nodes.quality_node import quality_node

def run_workflow(description: str, image_bytes: bytes, filename: str) -> str:
    """Executes the LangGraph workflow end-to-end."""
    graph = StateGraph(FashionState)

    # define flow
    graph.add_node("preprocess", preprocess_node)
    graph.add_node("prompt", prompt_node)
    graph.add_node("generate", generate_node)
    graph.add_node("quality", quality_node)

    graph.add_edge("preprocess", "prompt")
    graph.add_edge("prompt", "generate")
    graph.add_edge("generate", "quality")

    graph.set_entry_point("preprocess")

    chain = graph.compile()

    state = FashionState(description=description, product_image=image_bytes, filename=filename)
    final_state = chain.invoke(state)

    return final_state.output_path

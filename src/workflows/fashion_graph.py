from langgraph.graph import StateGraph, END
from models.state import FashionState
from workflows.nodes.prompt_node import prompt_node
from workflows.nodes.generate_node import generate_node
from workflows.nodes.quality_node import quality_node
import logging
from utils.file_utils import save_image

MAX_RETRIES = 2

def should_retry(state: FashionState) -> str:
    """
    A simple conditional edge. Decides whether to loop back to the
    generation node or to end the workflow.
    """
    logging.info("🚦 Checking condition: Should we retry generation?")
    
    assessment = state.quality_assessment
    if assessment and assessment.get("decision") == "accept":
        logging.info("👍 Condition met: Quality is good. Ending workflow.")
        return END
    
    if state.retry_count < MAX_RETRIES:
        logging.info(f"👎 Condition met: Quality is poor. Retrying (Attempt {state.retry_count + 1}).")
        return "regenerate"
    
    logging.error("🚫 Condition met: Max retries reached. Ending workflow.")
    return END

def run_workflow(description: str, image_bytes: bytes = None, filename: str = "generated.png") -> str:
    """
    Executes a simplified, robust workflow with a quality check loop.
    """
    graph = StateGraph(FashionState)

    # Define nodes
    graph.add_node("prompt", prompt_node)
    graph.add_node("generate", generate_node)
    graph.add_node("quality", quality_node)
    
    def increment_retry_counter(state: FashionState) -> dict:
        return {"retry_count": state.retry_count + 1}
    graph.add_node("increment_retry", increment_retry_counter)

    # Define edges
    graph.set_entry_point("prompt")
    graph.add_edge("prompt", "generate")
    graph.add_edge("generate", "quality")
    graph.add_edge("increment_retry", "generate")

    # Define conditional logic
    graph.add_conditional_edges(
        "quality",
        should_retry,
        {
            "regenerate": "increment_retry",
            END: END
        }
    )

    chain = graph.compile()
    
    initial_state = {
        "description": description,
        "product_image": image_bytes,
        "filename": filename,
        "mode": "image-to-image" if image_bytes else "text-to-image",
        "retry_count": 0,
    }

    final_state_dict = chain.invoke(initial_state)

    # Handle final output and save failed images
    output_path = final_state_dict.get("output_path")
    if output_path:
        logging.info("✅ Workflow completed successfully.")
        return output_path
    else:
        logging.error("❌ Workflow failed to produce a high-quality image after retries.")
        last_generated_image = final_state_dict.get("generated_image")
        if last_generated_image:
            logging.info("💾 Saving the last failed image to the 'failed' folder for review.")
            failure_path = save_image(last_generated_image, filename, "failed")
            return f"Workflow failed, but the last attempt was saved here: {failure_path}"
        
        return "Workflow failed and no image was produced."
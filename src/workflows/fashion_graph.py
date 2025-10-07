from langgraph.graph import StateGraph, END
from models.state import FashionState
from workflows.nodes.prompt_node import prompt_node
from workflows.nodes.generate_node import generate_node
from workflows.nodes.quality_node import quality_node
from workflows.nodes.text_correction_node import text_correction_node
import logging
from utils.file_utils import save_image

# --- General Settings ---
MAX_RETRIES = 2 # Maximum number of regeneration attempts

# --- Utility Nodes ---

def increment_retry_counter(state: FashionState) -> dict:
    """A simple utility node to increment the retry counter."""
    return {"retry_count": state.retry_count + 1}

def save_failed_image_node(state: FashionState) -> dict:
    """
    This is the terminal node that saves the last generated image to the 'failed'
    folder when the workflow fails definitively.
    """
    last_generated_image = state.generated_image
    if last_generated_image:
        logging.info("💾 Saving the last generated (failed) image for review...")
        failure_path = save_image(last_generated_image, state.filename, "failed")
        return {"output_path": f"Workflow failed, but the last attempt was saved here: {failure_path}"}
    return {"output_path": "Workflow failed and no image was produced."}

# --- The Brain of the Graph ---

def decide_next_step(state: FashionState) -> str:
    """
    This is the intelligent "brain" of the workflow.
    It decides the next step based on the detailed quality assessment.
    """
    logging.info("🚦 Brain: Deciding next step...")
    assessment = state.quality_assessment
    
    # 1. Golden Path: Everything is perfect
    if assessment.get("image_decision") == "accept" and assessment.get("text_decision") == "accept":
        logging.info("👍 Brain: Image and text are perfect. Ending workflow.")
        return "end_successfully"

    # 2. Second Path: Image is good, but text needs correction
    if assessment.get("image_decision") == "accept" and assessment.get("text_decision") == "reject":
        # Ensure we haven't already tried to correct the text, to avoid an infinite loop
        if not state.text_correction_applied:
            logging.info("🤔 Brain: Image is good, but text needs correction. Routing to Text Corrector.")
            return "correct_text"
        else:
            logging.warning("⚠️ Brain: Text correction was already applied and failed. Routing to failure save.")
            return "save_failure"

    # 3. Third Path: The image is poor and needs a full regeneration
    if state.retry_count < MAX_RETRIES:
        logging.info(f"👎 Brain: Image quality is poor. Retrying generation (Attempt {state.retry_count + 1}).")
        return "regenerate"
    
    # 4. Final Path: All retries have failed
    logging.error("🚫 Brain: Max retries reached. Routing to failure save.")
    return "save_failure"

# --- Main Workflow Orchestrator ---

def run_workflow(description: str, image_bytes: bytes = None, filename: str = "generated.png") -> str:
    """
    Executes the entire intelligent workflow, including quality checks,
    retry loops, and text correction.
    """
    graph = StateGraph(FashionState)

    # Add all nodes to the graph
    graph.add_node("prompt", prompt_node)
    graph.add_node("generate", generate_node)
    graph.add_node("quality", quality_node)
    graph.add_node("correct_text", text_correction_node)
    graph.add_node("increment_retry", increment_retry_counter)
    graph.add_node("save_failure", save_failed_image_node)

    # Define the edges (the flow of work) between nodes
    graph.set_entry_point("prompt")
    graph.add_edge("prompt", "generate")
    graph.add_edge("generate", "quality")
    graph.add_edge("correct_text", "quality") # After text correction, re-assess the quality
    graph.add_edge("increment_retry", "generate")
    graph.add_edge("save_failure", END) # The failure-saving node ends the process

    # Add the advanced conditional logic
    graph.add_conditional_edges(
        "quality",
        decide_next_step,
        {
            "regenerate": "increment_retry",
            "correct_text": "correct_text",
            "save_failure": "save_failure",
            "end_successfully": END 
        }
    )

    chain = graph.compile()
    
    # Initialize the state as a dictionary
    initial_state = {
        "description": description,
        "product_image": image_bytes,
        "filename": filename,
        "mode": "image-to-image" if image_bytes else "text-to-image",
        "retry_count": 0,
        "text_correction_applied": False
    }

    final_state_dict = chain.invoke(initial_state)

    # Handle the final output
    output_path = final_state_dict.get("output_path")
    
    if output_path and "failed" not in output_path:
        logging.info("✅ Workflow completed successfully.")
        return output_path
    elif output_path and "failed" in output_path:
        logging.error("❌ Workflow failed to produce a high-quality image.")
        return output_path
    else:
        # Unexpected case
        return "Workflow ended without a clear save path."
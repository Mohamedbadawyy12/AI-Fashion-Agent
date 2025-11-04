# AI-Fashion-Agent

AI-Fashion-Agent is an autonomous, multi-agent system designed to generate high-quality, professional fashion and product marketing images.

It takes a simple text description—and optionally, a product image—and uses a workflow powered by **LangGraph** and **Google Gemini** to create a polished visual. The system includes an AI quality assurance step that automatically reviews the generated image and triggers a re-generation loop if the quality is not met.

## Core Features

* **AI Creative Director**: Automatically enhances simple user prompts (e.g., "woman holding this cream") into rich, detailed photographic briefs using Gemini Pro.
* **Multi-Modal Generation**: Supports both text-to-image and image-to-image generation (using a product image as a base) with Gemini Flash.
* **Autonomous QA & Self-Correction**: A dedicated AI agent assesses each generated image against the creative brief for quality, product accuracy, and technical flaws.
* **Resilient Workflow**: Built with LangGraph, the agent automatically retries generation (up to a set maximum) if the AI QA agent "rejects" an image, ensuring a high-quality final output.
* **FastAPI Backend**: Exposed as a simple-to-use REST API built with FastAPI.

## How It Works: The Agent Workflow

This project uses `langgraph` to define a stateful graph that represents the agent's "thought process".

1.  **Ingest (API)**: The FastAPI server receives a `description` and an optional `product_image` at the `/generate` endpoint.
2.  **Enhance (`prompt_node`)**: The initial `description` is sent to the `gemini_prompt_enchancer` service. This service, acting as a "creative director," expands the simple text into a detailed, descriptive prompt suitable for an AI image generator.
3.  **Generate (`generate_node`)**: The new `enhanced_prompt` (and `product_image`, if provided) is sent to the `gemini_image_gen` service to create the image.
4.  **Assess (`quality_node`)**: The generated image, the prompt, and the original product image are all sent to the `gemini_quality_assessor` service. This AI QA agent inspects the image and returns a JSON object with a `"decision": "accept"` or `"decision": "reject"` and a `reason`.
5.  **Loop (Conditional Edge)**:
    * **If "accept"**: The workflow ends, and the image is saved to the `success` folder.
    * **If "reject"**: The `retry_count` is incremented. If the count is less than the max (`MAX_RETRIES`), the graph loops back to the `generate_node` for another attempt. If max retries are hit, the workflow ends, and the last failed image is saved for review.

## Tech Stack

* **Backend**: FastAPI
* **Agent Framework**: LangGraph
* **AI Models**: Google Gemini (Pro for prompt enhancement, Flash for image generation & QA)
* **Dependencies**: `langchain-google-genai`, `google-genai`, `Pillow`, `uvicorn`
* **Data Models**: Pydantic

## Getting Started

### 1. Prerequisites

* Python 3.9+
* A Google Gemini API Key

### 2. Installation

1.  Clone the repository:
    ```bash
    git clone [https://github.com/mohamedbadawyy12/ai-fashion-agent.git](https://github.com/mohamedbadawyy12/ai-fashion-agent.git)
    cd ai-fashion-agent
    ```

2.  Navigate to the `src` directory (as `requirements.txt` is located there):
    ```bash
    cd src
    ```

3.  Create and activate a virtual environment:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

4.  Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

### 3. Configuration

1.  This project uses a `.env` file to manage API keys. In the `src/` directory, create a file named `.env`.

2.  Add your Google API key to the `.env` file:
    ```
    GOOGLE_API_KEY="YOUR_GEMINI_API_KEY_HERE"
    ```

### 4. Running the Application

1.  From the `src/` directory, run the FastAPI server using Uvicorn:
    ```bash
    uvicorn main:app --reload
    ```

2.  The API will be live at `http://127.0.0.1:8000`.
3.  Access the interactive API documentation (Swagger UI) at `http://127.0.0.1:8000/docs`.

## API Usage

### Generate Image

Submit a request to the `/generate` endpoint to start the workflow.

* **URL**: `/api/v1/fashion/generate`
* **Method**: `POST`
* **Body**: `multipart/form-data`
    * `description` (string, required): A simple description of the image you want.
    * `product_image` (file, optional): An image file of the product to feature.

**Example using `curl`:**

```bash
# Text-to-Image
curl -X 'POST' \
  '[http://127.0.0.1:8000/api/v1/fashion/generate](http://127.0.0.1:8000/api/v1/fashion/generate)' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'description=A woman in a red dress'

# Image-to-Image
curl -X 'POST' \
  '[http://127.0.0.1:8000/api/v1/fashion/generate](http://127.0.0.1:8000/api/v1/fashion/generate)' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'description=A model holding this product in a studio' \
  -F 'product_image=@/path/to/your/product.png'

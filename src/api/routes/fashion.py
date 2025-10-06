from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from workflows.fashion_graph import run_workflow
from api.schemas import GenerateResponse

router = APIRouter()

@router.post("/generate", response_model=GenerateResponse)
async def generate(description: str = Form(...), product_image: UploadFile = File(...)):
    """
    Upload product image and description → run LangGraph workflow → return generated image path
    """
    try:
        contents = await product_image.read()
        output_path = run_workflow(description, contents, product_image.filename)
        return {"status": "success", "output_path": output_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

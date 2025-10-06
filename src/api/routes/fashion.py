from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional
from workflows.fashion_graph import run_workflow
from models.schemas import GenerateResponse

router = APIRouter()


@router.post("/generate", response_model=GenerateResponse)
async def generate(description: str = Form(...), product_image: Optional[UploadFile] = File(None)):
    """
    Upload product image (optional) + description → run workflow → return generated image path
    """
    try:
        image_bytes = None
        filename = "no_input.png"

        if product_image:
            image_bytes = await product_image.read()
            filename = product_image.filename

        output_path = run_workflow(description, image_bytes, filename)
        return {"status": "success", "output_path": output_path}

    except Exception as e:
        import traceback

        traceback.print_exc()  

        raise HTTPException(status_code=500, detail=str(e))

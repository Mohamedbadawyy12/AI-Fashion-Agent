from pydantic import BaseModel

class FashionState(BaseModel):
    description: str
    product_image: bytes
    filename: str
    enhanced_prompt: str = None
    generated_image: bytes = None
    output_path: str = None

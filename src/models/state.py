from pydantic import BaseModel
from typing import Optional, Dict

class FashionState(BaseModel):
    description: str
    product_image: Optional[bytes] = None
    filename: str
    mode: str  
    enhanced_prompt: Optional[str] = None
    generated_image: Optional[bytes] = None
    output_path: Optional[str] = None
    quality_assessment: Optional[Dict] = None
    retry_count: int = 0
    text_correction_applied: bool = False
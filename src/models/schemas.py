from pydantic import BaseModel


class GenerateRequest(BaseModel):
    description: str


class GenerateResponse(BaseModel):
    status: str
    output_path: str
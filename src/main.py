from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import fashion
import logging
from fastapi.staticfiles import StaticFiles
from pathlib import Path  


app = FastAPI(title="AI Fashion Agency")
BASE_DIR = Path(__file__).resolve().parent


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
logging.basicConfig(level=logging.INFO)
app.include_router(fashion.router, prefix="/api/v1/fashion", tags=["Fashion"])
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

@app.get("/")
async def root():
    return {"message": "AI Fashion Agency API is running 🚀"}

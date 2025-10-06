from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import fashion

app = FastAPI(title="AI Fashion Agency")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(fashion.router, prefix="/api/v1/fashion", tags=["Fashion"])

@app.get("/")
async def root():
    return {"message": "AI Fashion Agency API is running 🚀"}

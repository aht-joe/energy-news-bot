import uvicorn
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api import api_router, init_database

app = FastAPI(
    title="Energy News Bot API",
    description="API for managing energy news articles, keywords, and companies with relevance scoring and Teams integration",
    version="1.0.0",
    redirect_slashes=False
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    init_database()

@app.get("/")
async def root():
    return {"message": "Energy News Bot API", "docs": "/docs"}

app.include_router(api_router)

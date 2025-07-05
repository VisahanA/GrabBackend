"""
API v1 router configuration
"""

from fastapi import APIRouter

from app.api.v1.endpoints import ocr, speech_to_text, llm
from app.core.config import settings

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(
    ocr.router,
    prefix="/ocr",
    tags=["OCR"]
)

api_router.include_router(
    speech_to_text.router,
    prefix="/stt",
    tags=["Speech-to-Text"]
)

api_router.include_router(
    llm.router,
    prefix="/llm",
    tags=["LLM"]
) 
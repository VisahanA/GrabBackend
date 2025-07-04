"""
API v1 router configuration
"""

from fastapi import APIRouter

from app.api.v1.endpoints import ocr
from app.core.config import settings

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(
    ocr.router,
    prefix="/ocr",
    tags=["OCR"]
) 
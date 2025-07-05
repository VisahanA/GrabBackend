"""
Pydantic schemas for request and response validation
"""

from .ocr import OCRRequest, OCRResponse, TextBlock, ErrorResponse, OCRLanguage, ImageFormat
from .speech_to_text import (
    STTRequest, STTResponse, STTErrorResponse,
    AudioFormat
)
from .llm import LLMRequest, LLMResponse

__all__ = [
    "OCRRequest",
    "OCRResponse", 
    "TextBlock",
    "ErrorResponse",
    "OCRLanguage",
    "ImageFormat",
    "STTRequest",
    "STTResponse",
    "STTErrorResponse",
    "AudioFormat",
    "LLMRequest",
    "LLMResponse"
] 
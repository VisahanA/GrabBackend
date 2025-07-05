"""
Business logic services
"""

from .ocr_service import OCRService, ocr_service
from .speech_to_text_service import SpeechToTextService, stt_service

__all__ = ["OCRService", "ocr_service", "SpeechToTextService", "stt_service"] 
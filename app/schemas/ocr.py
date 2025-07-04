from pydantic import BaseModel, HttpUrl, Field
from typing import Optional, List
from enum import Enum


class OCRLanguage(str, Enum):
    """Supported OCR languages - English only"""
    ENGLISH = "eng"


class ImageFormat(str, Enum):
    """Supported image formats"""
    JPEG = "jpeg"
    JPG = "jpg"
    PNG = "png"
    BMP = "bmp"
    TIFF = "tiff"
    WEBP = "webp"


class OCRRequest(BaseModel):
    """Request schema for OCR API"""
    image_url: HttpUrl = Field(
        ..., 
        description="URL of the image to perform OCR on",
        example="https://garlicdelight.com/wp-content/uploads/20210319-reverse-shopping-list-768x768.png"
    )
    language: OCRLanguage = Field(
        default=OCRLanguage.ENGLISH,
        description="Language for OCR recognition"
    )
    confidence_threshold: Optional[float] = Field(
        default=0.0,
        ge=0.0,
        le=100.0,
        description="Minimum confidence threshold for text detection (0-100)"
    )
    preprocess_image: Optional[bool] = Field(
        default=True,
        description="Whether to preprocess the image for better OCR results"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "image_url": "https://garlicdelight.com/wp-content/uploads/20210319-reverse-shopping-list-768x768.png",
                "language": "eng",
                "confidence_threshold": 0.0,
                "preprocess_image": True
            }
        }


class TextBlock(BaseModel):
    """Individual text block detected in the image"""
    text: str = Field(..., description="Extracted text content")
    confidence: float = Field(..., description="Confidence score (0-100)")
    bounding_box: Optional[dict] = Field(
        default=None,
        description="Bounding box coordinates {x, y, width, height}"
    )


class OCRResponse(BaseModel):
    """Response schema for OCR API"""
    success: bool = Field(..., description="Whether the OCR operation was successful")
    extracted_text: str = Field(..., description="Full extracted text from the image")
    text_blocks: List[TextBlock] = Field(
        default=[],
        description="Individual text blocks with confidence scores"
    )
    total_confidence: float = Field(
        ..., 
        description="Overall confidence score for the entire extraction"
    )
    processing_time_ms: float = Field(..., description="Processing time in milliseconds")
    image_info: dict = Field(..., description="Information about the processed image")
    language_detected: str = Field(
        default="eng",
        description="Language of the text (always English)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "extracted_text": "Hello World! This is sample text.",
                "text_blocks": [
                    {
                        "text": "Hello World!",
                        "confidence": 95.5,
                        "bounding_box": {"x": 10, "y": 20, "width": 150, "height": 30}
                    },
                    {
                        "text": "This is sample text.",
                        "confidence": 88.2,
                        "bounding_box": {"x": 10, "y": 60, "width": 200, "height": 25}
                    }
                ],
                "total_confidence": 91.85,
                "processing_time_ms": 1250.5,
                "image_info": {
                    "width": 800,
                    "height": 600,
                    "format": "JPEG",
                    "mode": "RGB",
                    "size_bytes": 102400
                },
                "language_detected": "eng"
            }
        }


class ErrorResponse(BaseModel):
    """Error response schema"""
    success: bool = Field(default=False, description="Operation success status")
    error_code: str = Field(..., description="Error code identifier")
    error_message: str = Field(..., description="Human-readable error message")
    details: Optional[dict] = Field(default=None, description="Additional error details")

    class Config:
        json_schema_extra = {
            "example": {
                "success": False,
                "error_code": "INVALID_IMAGE_URL",
                "error_message": "The provided image URL is invalid or inaccessible",
                "details": {
                    "url": "https://garlicdelight.com/wp-content/uploads/20210319-reverse-shopping-list-768x768.png",
                    "status_code": 404
                }
            }
        } 
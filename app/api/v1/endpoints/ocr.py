"""
OCR API endpoints
"""

from fastapi import APIRouter, HTTPException, status
from typing import Union

from app.schemas.ocr import OCRRequest, OCRResponse, ErrorResponse
from app.services.ocr_service import ocr_service

router = APIRouter()


@router.post(
    "/extract-text",
    response_model=OCRResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Bad Request"},
        422: {"model": ErrorResponse, "description": "Validation Error"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"}
    },
    summary="Extract text from image",
    description="""
    Extract text from an image using OCR (Optical Character Recognition).
    
    This endpoint accepts an image URL and returns the extracted text along with
    confidence scores and bounding box information for each detected text block.
    
    **Features:**
    - English language OCR support
    - Confidence threshold filtering
    - Image preprocessing for better accuracy
    - Detailed text block information with bounding boxes
    
    **Supported Image Formats:**
    - JPEG, PNG, BMP, TIFF, WEBP
    - Maximum file size: 10MB
    """
)
async def extract_text_from_image(request: OCRRequest) -> OCRResponse:
    """
    Extract text from an image using OCR
    
    Args:
        request: OCR request containing image URL and processing options
        
    Returns:
        OCRResponse: Extracted text with confidence scores and metadata
        
    Raises:
        HTTPException: For various error conditions
    """
    try:
        # Process the OCR request
        result = await ocr_service.process_ocr_request(request)
        return result
        
    except Exception as e:
        error_message = str(e)
        
        # Parse error code from the exception message
        if ":" in error_message:
            error_parts = error_message.split(":", 1)
            error_code = error_parts[0].strip()
            error_detail = error_parts[1].strip()
        else:
            error_code = "UNKNOWN_ERROR"
            error_detail = error_message
        
        # Determine HTTP status code based on error type
        if error_code == "IMAGE_DOWNLOAD_ERROR":
            status_code = status.HTTP_400_BAD_REQUEST
        elif error_code == "INVALID_IMAGE_FORMAT":
            status_code = status.HTTP_400_BAD_REQUEST
        elif error_code == "IMAGE_TOO_LARGE":
            status_code = status.HTTP_413_REQUEST_ENTITY_TOO_LARGE
        elif error_code == "OCR_PROCESSING_ERROR":
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        else:
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        
        # Create error response
        error_response = ErrorResponse(
            success=False,
            error_code=error_code,
            error_message=error_detail,
            details={
                "image_url": str(request.image_url),
                "language": request.language.value,
                "confidence_threshold": request.confidence_threshold
            }
        )
        
        raise HTTPException(
            status_code=status_code,
            detail=error_response.dict()
        )


@router.get(
    "/health",
    summary="Health check",
    description="Check if the OCR service is healthy and operational"
)
async def health_check():
    """
    Health check endpoint for the OCR service
    
    Returns:
        dict: Health status information
    """
    try:
        # You could add more sophisticated health checks here
        # For example, test if EasyOCR is available and working
        import easyocr
        
        return {
            "status": "healthy",
            "service": "OCR API",
            "ocr_engine": "EasyOCR",
            "timestamp": "2024-01-01T00:00:00Z"  # In production, use datetime.utcnow()
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "OCR API",
            "error": str(e),
            "timestamp": "2024-01-01T00:00:00Z"  # In production, use datetime.utcnow()
        }


@router.get(
    "/supported-languages",
    summary="Get supported OCR languages",
    description="Returns a list of all supported languages for OCR processing"
)
async def get_supported_languages():
    """
    Get list of supported OCR languages
    
    Returns:
        dict: List of supported languages with their codes
    """
    from app.schemas.ocr import OCRLanguage
    
    languages = {}
    for lang in OCRLanguage:
        # Map language codes to readable names - English only
        language_names = {
            "eng": "English"
        }
        
        languages[lang.value] = language_names.get(lang.value, lang.value)
    
    return {
        "supported_languages": languages,
        "default_language": "eng"
    } 
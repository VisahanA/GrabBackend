"""
Speech-to-Text API endpoints
"""

from fastapi import APIRouter, HTTPException, status, UploadFile, File, Form
from typing import Union, Optional

from app.schemas.speech_to_text import STTRequest, STTResponse, STTErrorResponse, STTFileRequest
from app.services.speech_to_text_service import stt_service

router = APIRouter()


@router.post(
    "/transcribe",
    response_model=STTResponse,
    responses={
        400: {"model": STTErrorResponse, "description": "Bad Request"},
        422: {"model": STTErrorResponse, "description": "Validation Error"},
        500: {"model": STTErrorResponse, "description": "Internal Server Error"}
    },
    summary="Transcribe audio to text",
    description="""
    Transcribe audio to text using Speech Recognition.
    
    This endpoint accepts an audio URL and returns the transcribed text along with
    confidence scores and optional word-level timestamps and speaker diarization.
    
    **Features:**
    - English language support only
    - Confidence threshold filtering
    - Audio preprocessing for better accuracy
    
    **Supported Audio Formats:**
    - WAV, MP3, M4A, FLAC, OGG
    - Maximum file size: 25MB
    """
)
async def transcribe_audio(request: STTRequest) -> STTResponse:
    """
    Transcribe audio to text using Speech Recognition
    
    Args:
        request: STT request containing audio URL and processing options
        
    Returns:
        STTResponse: Transcribed text with confidence scores and metadata
        
    Raises:
        HTTPException: For various error conditions
    """
    try:
        # Process the STT request
        result = await stt_service.process_stt_request(request)
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
        if error_code == "AUDIO_DOWNLOAD_ERROR":
            status_code = status.HTTP_400_BAD_REQUEST
        elif error_code == "INVALID_AUDIO_FORMAT":
            status_code = status.HTTP_400_BAD_REQUEST
        elif error_code == "AUDIO_TOO_LARGE":
            status_code = status.HTTP_413_REQUEST_ENTITY_TOO_LARGE
        elif error_code == "SPEECH_RECOGNITION_ERROR":
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        else:
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        
        # Create error response
        error_response = STTErrorResponse(
            success=False,
            error_code=error_code,
            error_message=error_detail,
            details={
                "audio_url": str(request.audio_url),
                "confidence_threshold": request.confidence_threshold
            }
        )
        
        raise HTTPException(
            status_code=status_code,
            detail=error_response.dict()
        )


@router.post(
    "/transcribe-file",
    response_model=STTResponse,
    responses={
        400: {"model": STTErrorResponse, "description": "Bad Request"},
        422: {"model": STTErrorResponse, "description": "Validation Error"},
        500: {"model": STTErrorResponse, "description": "Internal Server Error"}
    },
    summary="Transcribe audio file to text",
    description="""
    Transcribe audio file to text using Speech Recognition.
    
    This endpoint accepts a direct audio file upload and returns the transcribed text along with
    confidence scores and processing metadata.
    
    **Features:**
    - English language support only
    - Confidence threshold filtering
    - Audio preprocessing for better accuracy
    - Direct file upload support
    
    **Supported Audio Formats:**
    - WAV, MP3, M4A, FLAC, OGG
    - Maximum file size: 25MB
    """
)
async def transcribe_audio_file(
    audio_file: UploadFile = File(..., description="Audio file to transcribe"),
    confidence_threshold: Optional[float] = Form(0.0, ge=0.0, le=100.0, description="Minimum confidence threshold (0-100)")
) -> STTResponse:
    """
    Transcribe audio file to text using Speech Recognition
    
    Args:
        audio_file: Uploaded audio file
        confidence_threshold: Minimum confidence threshold for word detection (0-100)
        
    Returns:
        STTResponse: Transcribed text with confidence scores and metadata
        
    Raises:
        HTTPException: For various error conditions
    """
    try:
        # Create file request object
        file_request = STTFileRequest(confidence_threshold=confidence_threshold)
        
        # Process the uploaded file
        result = await stt_service.process_uploaded_file_request(audio_file, file_request)
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
        if error_code == "AUDIO_UPLOAD_ERROR":
            status_code = status.HTTP_400_BAD_REQUEST
        elif error_code == "INVALID_AUDIO_FORMAT":
            status_code = status.HTTP_400_BAD_REQUEST
        elif error_code == "AUDIO_TOO_LARGE":
            status_code = status.HTTP_413_REQUEST_ENTITY_TOO_LARGE
        elif error_code == "SPEECH_RECOGNITION_ERROR":
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        else:
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        
        # Create error response
        error_response = STTErrorResponse(
            success=False,
            error_code=error_code,
            error_message=error_detail,
            details={
                "filename": audio_file.filename,
                "confidence_threshold": confidence_threshold
            }
        )
        
        raise HTTPException(
            status_code=status_code,
            detail=error_response.dict()
        )


@router.get(
    "/health",
    summary="Health check",
    description="Check if the Speech-to-Text service is healthy and operational"
)
async def health_check():
    """
    Health check endpoint for the Speech-to-Text service
    
    Returns:
        dict: Health status information
    """
    try:
        # You could add more sophisticated health checks here
        # For example, test if SpeechRecognition is available and working
        import speech_recognition
        
        return {
            "status": "healthy",
            "service": "Speech-to-Text API",
            "stt_engine": "SpeechRecognition (Google)",
            "timestamp": "2024-01-01T00:00:00Z"  # In production, use datetime.utcnow()
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "Speech-to-Text API",
            "error": str(e),
            "timestamp": "2024-01-01T00:00:00Z"  # In production, use datetime.utcnow()
        }


@router.get(
    "/supported-formats",
    summary="Get supported audio formats",
    description="Returns a list of all supported audio formats for transcription"
)
async def get_supported_formats():
    """
    Get list of supported audio formats
    
    Returns:
        dict: List of supported audio formats
    """
    from app.schemas.speech_to_text import AudioFormat
    
    formats = {}
    for fmt in AudioFormat:
        format_names = {
            "wav": "WAV (Waveform Audio)",
            "mp3": "MP3 (MPEG Audio)",
            "m4a": "M4A (MPEG-4 Audio)",
            "flac": "FLAC (Free Lossless Audio Codec)",
            "ogg": "OGG (Ogg Vorbis)"
        }
        
        formats[fmt.value] = format_names.get(fmt.value, fmt.value)
    
    return {
        "supported_formats": formats,
        "max_file_size_mb": 25
    } 
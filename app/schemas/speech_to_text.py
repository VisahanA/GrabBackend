from pydantic import BaseModel, HttpUrl, Field
from typing import Optional, List, Union
from enum import Enum


class AudioFormat(str, Enum):
    """Supported audio formats"""
    WAV = "wav"
    MP3 = "mp3"
    M4A = "m4a"
    FLAC = "flac"
    OGG = "ogg"


class STTRequest(BaseModel):
    """Request schema for Speech-to-Text API (English only)"""
    audio_url: HttpUrl = Field(
        ..., 
        description="URL of the audio file to transcribe",
        example="https://example.com/audio/sample.wav"
    )
    confidence_threshold: Optional[float] = Field(
        default=0.0,
        ge=0.0,
        le=100.0,
        description="Minimum confidence threshold for word detection (0-100)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "audio_url": "https://example.com/audio/sample.wav",
                "confidence_threshold": 0.0
            }
        }


class STTFileRequest(BaseModel):
    """Request schema for Speech-to-Text API with file upload"""
    confidence_threshold: Optional[float] = Field(
        default=0.0,
        ge=0.0,
        le=100.0,
        description="Minimum confidence threshold for word detection (0-100)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "confidence_threshold": 0.0
            }
        }


class STTResponse(BaseModel):
    """Response schema for Speech-to-Text API"""
    success: bool = Field(..., description="Whether the transcription was successful")
    transcribed_text: str = Field(..., description="Full transcribed text from the audio")
    total_confidence: float = Field(
        ..., 
        description="Overall confidence score for the entire transcription"
    )
    processing_time_ms: float = Field(..., description="Processing time in milliseconds")
    audio_info: dict = Field(..., description="Information about the processed audio")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "transcribed_text": "Hello world! This is a sample audio transcription.",
                "total_confidence": 91.85,
                "processing_time_ms": 2500.5,
                "audio_info": {
                    "duration": 2.5,
                    "format": "WAV",
                    "sample_rate": 16000,
                    "channels": 1,
                    "size_bytes": 204800
                }
            }
        }


class STTErrorResponse(BaseModel):
    """Error response schema for Speech-to-Text API"""
    success: bool = Field(default=False, description="Operation success status")
    error_code: str = Field(..., description="Error code identifier")
    error_message: str = Field(..., description="Human-readable error message")
    details: Optional[dict] = Field(default=None, description="Additional error details")

    class Config:
        json_schema_extra = {
            "example": {
                "success": False,
                "error_code": "INVALID_AUDIO_URL",
                "error_message": "The provided audio URL is invalid or inaccessible",
                "details": {
                    "url": "https://example.com/audio/sample.wav",
                    "status_code": 404
                }
            }
        } 
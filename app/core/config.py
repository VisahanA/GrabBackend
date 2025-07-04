"""
Core configuration settings for the OCR API
"""

import os
from typing import List
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "OCR API"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "A robust English-only OCR API that extracts text from images using EasyOCR"
    
    # Server Settings
    HOST: str = Field(default="0.0.0.0", env="HOST")
    PORT: int = Field(default=8000, env="PORT")
    DEBUG: bool = Field(default=False, env="DEBUG")
    
    # CORS Settings
    ALLOWED_ORIGINS: List[str] = Field(
        default=["*"], 
        env="ALLOWED_ORIGINS"
    )
    
    # OCR Settings
    MAX_IMAGE_SIZE_MB: int = Field(default=10, env="MAX_IMAGE_SIZE_MB")
    DEFAULT_OCR_LANGUAGE: str = Field(default="eng", env="DEFAULT_OCR_LANGUAGE")
    IMAGE_DOWNLOAD_TIMEOUT: int = Field(default=30, env="IMAGE_DOWNLOAD_TIMEOUT")
    
    # EasyOCR Settings
    USE_GPU: bool = Field(
        default=False, 
        env="USE_GPU",
        description="Whether to use GPU acceleration for EasyOCR (requires CUDA)"
    )
    
    # Rate Limiting (for future implementation)
    RATE_LIMIT_PER_MINUTE: int = Field(default=60, env="RATE_LIMIT_PER_MINUTE")
    
    # Logging
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings() 
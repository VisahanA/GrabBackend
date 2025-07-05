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
    PROJECT_NAME: str = "OCR & Speech-to-Text API"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "A robust API that extracts text from images using OCR and transcribes audio to text using Speech Recognition"
    
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
    
    # SpeechToText Settings
    MAX_AUDIO_SIZE_MB: int = Field(default=25, env="MAX_AUDIO_SIZE_MB")
    AUDIO_DOWNLOAD_TIMEOUT: int = Field(default=30, env="AUDIO_DOWNLOAD_TIMEOUT")
    SUPPORTED_AUDIO_FORMATS: List[str] = Field(
        default=["wav", "mp3", "m4a", "flac", "ogg"],
        env="SUPPORTED_AUDIO_FORMATS"
    )
    
    # LLM Settings
    DEFAULT_LLM_MODEL_ID: str = Field(
        default="anthropic.claude-3-5-sonnet-20241022-v2:0",
        env="DEFAULT_LLM_MODEL_ID",
        description="Default Bedrock model ID for LLM service"
    )
    DEFAULT_MAX_TOKENS: int = Field(
        default=512,
        ge=1,
        le=4096,
        env="DEFAULT_MAX_TOKENS",
        description="Default maximum tokens for LLM generation"
    )
    DEFAULT_TEMPERATURE: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        env="DEFAULT_TEMPERATURE",
        description="Default temperature for LLM generation"
    )
    DEFAULT_TOP_P: float = Field(
        default=0.01,
        ge=0.0,
        le=1.0,
        env="DEFAULT_TOP_P",
        description="Default top-p sampling parameter"
    )
    DEFAULT_TOP_K: int = Field(
        default=0,
        ge=0,
        env="DEFAULT_TOP_K",
        description="Default top-k sampling parameter"
    )
    BASE_PROMPT: str = Field(
        default="You are a shopping cart curator for an online hypermarket. Given the text from user, understand the intent and list only the category of items required, quantity or brand name not required. If you are given a list of items as such, then process the words with fuzzy match and return the list of items. If given a task of procurement of items then start the list with the essentials and then move on to other items. Return only a list of items, no explanation required. \nUser: \"milk, chiz, aniyan, carrot, ek\"\nAssistant : [\"milk\", \"cheese\", \"onion\", \"carrot\", \"egg\"]\nUser : \"I am wearing sambar today and please talk me the items. I already have brinjal, turmeric powder\"\nAssisant: [\"Toor Dal\", \"Tomato\", \"Onion\", \"Shallots\", \"Carrots\", \"Drumstick\", \"Tamarind\", \"Sambar powder\", \"Mustard seeds\", \"oil\", \"chilli\"]\nUser: \"Today is Sadya. Need items for lunch\"\nAssistant: [\"Raw Rice\", \"Toor Dal\", \"Coconut\", \"Green Chilies\", \"Ginger\", \"Curry Leaves\", \"Mustard Seeds\", \"Dried Red Chilies\", \"Tamarind\", \"Vegetables\", \"Yogurt\", \"Jaggery\", \"Cumin Seeds\", \"Coconut Oil\", \"Banana\", \"Papadam\", \"Pickles\"]\nUser: \"Today is my niece's birthday. she is of age 10. gifts for her\"\nAssistant: [\"Toys\", \"Chocolates\", \"Craft Kits\"]\nUser: \"{user_prompt}\"",
        env="BASE_PROMPT",
        description="Base prompt prefix to prepend to all user requests"
    )
    
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

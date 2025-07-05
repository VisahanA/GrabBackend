from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class LLMRequest(BaseModel):
    """Request schema for LLM service"""
    prompt: str = Field(..., description="The input prompt for the LLM")

class LLMResponse(BaseModel):
    """Response schema for LLM service"""
    generated_text: str = Field(..., description="The generated text from the LLM")
    model_id: str = Field(..., description="The model ID used for generation")
    max_tokens: int = Field(..., description="Maximum tokens requested")
    temperature: float = Field(..., description="Temperature used for generation")
    processing_time_ms: float = Field(..., description="Processing time in milliseconds")
    usage: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Token usage information if available"
    ) 
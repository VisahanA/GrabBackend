from fastapi import APIRouter, HTTPException, Depends
from app.schemas.llm import LLMRequest, LLMResponse
from app.services.llm_service import LLMService
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

def get_llm_service() -> LLMService:
    """Dependency to get LLM service instance"""
    return LLMService()

@router.post("/generate", response_model=LLMResponse, summary="Generate text using LLM")
async def generate_text(
    request: LLMRequest,
    llm_service: LLMService = Depends(get_llm_service)
) -> LLMResponse:
    """
    Generate text using Amazon Bedrock LLM models.
    
    This endpoint accepts a prompt to generate text using the configured
    LLM model and parameters from the application configuration.
    
    **Parameters:**
    - **prompt**: The input text prompt for the LLM
    
    **Returns:**
    - **generated_text**: The generated text from the LLM
    - **model_id**: The model ID used for generation (from config)
    - **max_tokens**: Maximum tokens requested (from config)
    - **temperature**: Temperature used for generation (from config)
    - **processing_time_ms**: Processing time in milliseconds
    - **usage**: Token usage information if available
    """
    try:
        logger.info(f"Received LLM generation request with {len(request.prompt)} characters")
        
        # Generate text using the LLM service
        response = llm_service.generate_text(request)
        
        logger.info(f"Successfully generated text with {len(response.generated_text)} characters")
        return response
        
    except Exception as e:
        logger.error(f"Error generating text: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate text: {str(e)}"
        )

@router.get("/health", summary="Check LLM service health")
async def health_check(llm_service: LLMService = Depends(get_llm_service)) -> dict:
    """
    Check the health of the LLM service by testing AWS Bedrock connection.
    
    **Returns:**
    - **status**: Service status ("healthy" or "unhealthy")
    - **message**: Status message
    """
    try:
        is_healthy = llm_service.test_connection()
        
        if is_healthy:
            return {
                "status": "healthy",
                "message": "LLM service is operational and connected to AWS Bedrock"
            }
        else:
            return {
                "status": "unhealthy", 
                "message": "LLM service cannot connect to AWS Bedrock"
            }
            
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "message": f"Health check failed: {str(e)}"
        } 
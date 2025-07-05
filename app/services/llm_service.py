import boto3
import json
import time
import logging
from typing import Dict, Any, Optional
from botocore.exceptions import ClientError
from app.schemas.llm import LLMRequest, LLMResponse
from app.core.config import settings

logger = logging.getLogger(__name__)

class LLMService:
    """Service for interacting with Amazon Bedrock LLM models"""
    
    def __init__(self):
        """Initialize the LLM service with AWS Bedrock client"""
        try:
            # Import AWS credentials
            import aws_credentials
            
            self.client = boto3.client(
                service_name=aws_credentials.AWS_SERVICE_NAME,
                region_name=aws_credentials.AWS_DEFAULT_REGION,
                aws_access_key_id=aws_credentials.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=aws_credentials.AWS_SECRET_ACCESS_KEY,
                aws_session_token=aws_credentials.AWS_SESSION_TOKEN
            )
            logger.info("LLM service initialized successfully with AWS Bedrock")
            
        except ImportError:
            logger.error("aws_credentials module not found. Please create aws_credentials.py with your AWS credentials.")
            raise
        except Exception as e:
            logger.error(f"Failed to initialize LLM service: {e}")
            raise
    
    def generate_text(self, request: LLMRequest) -> LLMResponse:
        """
        Generate text using Amazon Bedrock
        
        Args:
            request: LLMRequest object containing prompt and parameters
            
        Returns:
            LLMResponse object with generated text and metadata
        """
        start_time = time.time()
        
        try:
            # Replace user_prompt placeholder in BASE_PROMPT with actual user prompt
            full_prompt = settings.BASE_PROMPT.format(user_prompt=request.prompt)
            
            # Format the request payload using the model's native structure
            native_request = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": settings.DEFAULT_MAX_TOKENS,
                "temperature": settings.DEFAULT_TEMPERATURE,
                "top_p": settings.DEFAULT_TOP_P,
                "top_k": settings.DEFAULT_TOP_K,
                "messages": [
                    {
                        "role": "user",
                        "content": [{"type": "text", "text": full_prompt}],
                    }
                ],
            }
            
            # Convert the native request to JSON
            request_body = json.dumps(native_request)
            
            logger.info(f"Invoking model {settings.DEFAULT_LLM_MODEL_ID} with {settings.DEFAULT_MAX_TOKENS} max tokens")
            
            # Invoke the model
            response = self.client.invoke_model(
                modelId=settings.DEFAULT_LLM_MODEL_ID,
                body=request_body
            )
            
            # Decode the response body
            model_response = json.loads(response["body"].read())
            
            # Extract the response text
            generated_text = model_response["content"][0]["text"]
            
            # Calculate processing time
            processing_time_ms = (time.time() - start_time) * 1000
            
            # Extract usage information if available
            usage = None
            if "usage" in model_response:
                usage = model_response["usage"]
            
            logger.info(f"Successfully generated text in {processing_time_ms:.2f}ms")
            
            return LLMResponse(
                generated_text=generated_text,
                model_id=settings.DEFAULT_LLM_MODEL_ID,
                max_tokens=settings.DEFAULT_MAX_TOKENS,
                temperature=settings.DEFAULT_TEMPERATURE,
                processing_time_ms=processing_time_ms,
                usage=usage
            )
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            logger.error(f"AWS Bedrock error ({error_code}): {error_message}")
            raise Exception(f"Bedrock API error: {error_message}")
            
        except Exception as e:
            logger.error(f"Unexpected error during text generation: {e}")
            raise Exception(f"Text generation failed: {str(e)}")
    
    def test_connection(self) -> bool:
        """
        Test the connection to AWS Bedrock
        
        Returns:
            bool: True if connection is successful, False otherwise
        """
        try:
            # Try to list available models to test connection
            response = self.client.list_foundation_models()
            logger.info("AWS Bedrock connection test successful")
            return True
        except Exception as e:
            logger.error(f"AWS Bedrock connection test failed: {e}")
            return False 
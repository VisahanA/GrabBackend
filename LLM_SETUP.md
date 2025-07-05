# LLM Service Setup Guide

This guide explains how to set up and use the LLM service that integrates with Amazon Bedrock.

## Prerequisites

1. **AWS Account**: You need an AWS account with access to Amazon Bedrock
2. **AWS Credentials**: Configure your AWS credentials
3. **Python Dependencies**: Install the required packages

## Setup Steps

### 1. Install Dependencies

```bash
pip install boto3==1.34.0
```

Or install all requirements:
```bash
pip install -r requirements.txt
```

### 2. Configure AWS Credentials

Create a file named `aws_credentials.py` in your project root with the following structure:

```python
# AWS Bedrock Configuration
AWS_SERVICE_NAME = "bedrock-runtime"
AWS_DEFAULT_REGION = "us-east-1"  # or your preferred region
AWS_ACCESS_KEY_ID = "your-access-key-id"
AWS_SECRET_ACCESS_KEY = "your-secret-access-key"
AWS_SESSION_TOKEN = "your-session-token"  # Optional for temporary credentials
```

### 3. AWS Bedrock Access

Ensure your AWS account has access to Amazon Bedrock and the specific models you want to use. The default model is:
- `anthropic.claude-3-5-sonnet-20241022-v2:0`

### 4. Start the Service

```bash
python run.py
```

The LLM service will be available at:
- **Generate Text**: `POST /api/v1/llm/generate`
- **Health Check**: `GET /api/v1/llm/health`

## API Usage

### Generate Text

**Endpoint**: `POST /api/v1/llm/generate`

**Request Body**:
```json
{
    "prompt": "Write a short paragraph about artificial intelligence."
}
```

**Response**:
```json
{
    "generated_text": "Artificial intelligence (AI) is a branch of computer science...",
    "model_id": "anthropic.claude-3-5-sonnet-20241022-v2:0",
    "max_tokens": 100,
    "temperature": 0.7,
    "processing_time_ms": 1234.56,
    "usage": {
        "input_tokens": 15,
        "output_tokens": 45
    }
}
```

### Health Check

**Endpoint**: `GET /api/v1/llm/health`

**Response**:
```json
{
    "status": "healthy",
    "message": "LLM service is operational and connected to AWS Bedrock"
}
```

## Testing

Run the test script to verify the service:

```bash
python tests/test_llm.py
```

## Configuration

The LLM service uses the following configuration parameters (set in `app/core/config.py` or environment variables):

- **DEFAULT_LLM_MODEL_ID**: Bedrock model ID (default: `anthropic.claude-3-5-sonnet-20241022-v2:0`)
- **DEFAULT_MAX_TOKENS**: Maximum tokens to generate (1-4096, default: 512)
- **DEFAULT_TEMPERATURE**: Controls randomness (0.0-1.0, default: 0.5)
- **DEFAULT_TOP_P**: Top-p sampling (0.0-1.0, default: 0.01)
- **DEFAULT_TOP_K**: Top-k sampling (0+, default: 0)
- **BASE_PROMPT**: Base prompt prefix to prepend to all user requests (default: "You are a helpful AI assistant. Please respond to the following request:")

**Example BASE_PROMPT configurations:**
```bash
# Default helpful assistant
BASE_PROMPT="You are a helpful AI assistant. Please respond to the following request:"

# Technical writer
BASE_PROMPT="You are an expert technical writer. Write clear, concise responses to the following questions:"

# Code assistant
BASE_PROMPT="You are a programming expert. Provide code examples and explanations for the following:"

# Creative writer
BASE_PROMPT="You are a creative writer. Write engaging and imaginative responses to the following prompts:"
```

## Parameters

- **prompt** (required): The input text for the LLM

## Error Handling

The service includes comprehensive error handling for:
- AWS credential issues
- Bedrock API errors
- Invalid parameters
- Network connectivity issues

## Security Notes

- Keep your AWS credentials secure
- Use IAM roles with minimal required permissions
- Consider using AWS Secrets Manager for production deployments
- Monitor API usage and costs 
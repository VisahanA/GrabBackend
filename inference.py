import boto3
import json
import aws_credentials
from botocore.exceptions import ClientError

client = boto3.client(
  service_name= aws_credentials.AWS_SERVICE_NAME, 
  region_name= aws_credentials.AWS_DEFAULT_REGION,
  aws_access_key_id= aws_credentials.AWS_ACCESS_KEY_ID,
  aws_secret_access_key= aws_credentials.AWS_SECRET_ACCESS_KEY,
  aws_session_token= aws_credentials.AWS_SESSION_TOKEN
)

prompt = "Write a medium blog post on how to use Amazon Bedrock to write an article on how to use Bedrock."

body = json.dumps({
    "prompt": prompt,python run.py
    "max_tokens_to_sample": 1000,
    "temperature": 0.75,
    "top_p": 0.01,
    "top_k": 0
})

model_id = 'anthropic.claude-3-5-sonnet-20241022-v2:0'
accept = 'application/json'
contentType = 'application/json'

# Format the request payload using the model's native structure.
native_request = {
    "anthropic_version": "bedrock-2023-05-31",
    "max_tokens": 512,
    "temperature": 0.5,
    "messages": [
        {
            "role": "user",
            "content": [{"type": "text", "text": prompt}],
        }
    ],
}

# Convert the native request to JSON.
request = json.dumps(native_request)

try:
    # Invoke the model with the request.
    response = client.invoke_model(modelId=model_id, body=request)

except (ClientError, Exception) as e:
    print(f"ERROR: Can't invoke '{model_id}'. Reason: {e}")
    exit(1)

# Decode the response body.
model_response = json.loads(response["body"].read())

# Extract and print the response text.
response_text = model_response["content"][0]["text"]
print(response_text)
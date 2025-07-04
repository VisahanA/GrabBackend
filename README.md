# OCR API

A robust FastAPI-based OCR (Optical Character Recognition) API that extracts text from images using EasyOCR.

## Features

- 🔤 **English OCR support** - Specialized for English language text recognition
- 📸 **Multiple image formats** - Supports JPEG, PNG, BMP, TIFF, and WEBP formats
- 🎯 **Confidence scoring** - Returns confidence scores for extracted text blocks
- 📍 **Bounding box detection** - Provides precise location coordinates for each text block
- 🔧 **Image preprocessing** - Automatic image enhancement for better OCR accuracy
- 🌐 **URL-based processing** - Process images directly from URLs
- 📝 **Detailed metadata** - Returns image information and processing statistics
- 🧪 **Well-tested** - Comprehensive test suite with mocking
- 📚 **Auto-generated documentation** - Interactive API docs with Swagger UI

## Project Structure

```
GrabBackend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── api/
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── api.py          # API router configuration
│   │       └── endpoints/
│   │           ├── __init__.py
│   │           └── ocr.py      # OCR endpoints
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py           # Application configuration
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── ocr.py              # Pydantic schemas
│   └── services/
│       ├── __init__.py
│       └── ocr_service.py      # OCR business logic
├── tests/
│   ├── __init__.py
│   └── test_ocr.py             # Test cases
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## Prerequisites

### System Requirements

- Python 3.8+
- **No additional system dependencies required!** EasyOCR works out of the box.

### GPU Support (Optional)
For faster processing, you can enable GPU acceleration if you have:
- NVIDIA GPU with CUDA support
- PyTorch with CUDA support

Set the `USE_GPU=true` environment variable to enable GPU acceleration.

## Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd GrabBackend
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables** (optional)
```bash
# Copy example configuration
cp .env.example .env

# Edit .env file with your settings
```

## Configuration

The API can be configured using environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST` | `0.0.0.0` | Server host |
| `PORT` | `8000` | Server port |
| `DEBUG` | `false` | Debug mode |
| `MAX_IMAGE_SIZE_MB` | `10` | Maximum image size in MB |
| `DEFAULT_OCR_LANGUAGE` | `eng` | Default OCR language |
| `IMAGE_DOWNLOAD_TIMEOUT` | `30` | Image download timeout (seconds) |
| `USE_GPU` | `false` | Enable GPU acceleration for EasyOCR |
| `ALLOWED_ORIGINS` | `*` | CORS allowed origins |
| `RATE_LIMIT_PER_MINUTE` | `60` | Rate limit per minute |
| `LOG_LEVEL` | `INFO` | Logging level |

## Running the API

### Development Mode
```bash
# From project root
python -m app.main

# Or with uvicorn directly
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/api/v1/docs
- **ReDoc**: http://localhost:8000/api/v1/redoc
- **OpenAPI JSON**: http://localhost:8000/api/v1/openapi.json

## API Endpoints

### Core Endpoints

#### `POST /api/v1/ocr/extract-text`
Extract text from an image URL.

**Request Body:**
```json
{
  "image_url": "https://example.com/image.jpg",
  "language": "eng",
  "confidence_threshold": 60.0,
  "preprocess_image": true
}
```

**Response:**
```json
{
  "success": true,
  "extracted_text": "Hello World! This is sample text.",
  "text_blocks": [
    {
      "text": "Hello World!",
      "confidence": 95.5,
      "bounding_box": {
        "x": 10,
        "y": 20,
        "width": 150,
        "height": 30
      }
    }
  ],
  "total_confidence": 91.85,
  "processing_time_ms": 1250.5,
  "image_info": {
    "width": 800,
    "height": 600,
    "format": "JPEG",
    "mode": "RGB",
    "size_bytes": 102400
  },
  "language_detected": "eng"
}
```

#### `GET /api/v1/ocr/supported-languages`
Get list of supported OCR languages.

#### `GET /api/v1/ocr/health`
Health check for OCR service.

### Utility Endpoints

#### `GET /`
API information and links.

#### `GET /health`
Basic health check.

## Usage Examples

### Python with requests
```python
import requests

# Extract text from image
response = requests.post(
    "http://localhost:8000/api/v1/ocr/extract-text",
    json={
        "image_url": "https://example.com/sample-image.jpg",
        "language": "eng",
        "confidence_threshold": 70.0,
        "preprocess_image": True
    }
)

result = response.json()
print(f"Extracted text: {result['extracted_text']}")
print(f"Confidence: {result['total_confidence']:.2f}%")
```

### cURL
```bash
curl -X POST "http://localhost:8000/api/v1/ocr/extract-text" \
  -H "Content-Type: application/json" \
  -d '{
    "image_url": "https://example.com/image.jpg",
    "language": "eng",
    "confidence_threshold": 70.0,
    "preprocess_image": true
  }'
```

### JavaScript/Node.js
```javascript
const response = await fetch('http://localhost:8000/api/v1/ocr/extract-text', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    image_url: 'https://example.com/image.jpg',
    language: 'eng',
    confidence_threshold: 70.0,
    preprocess_image: true
  })
});

const result = await response.json();
console.log('Extracted text:', result.extracted_text);
```

## Supported Languages

| Language | Code |
|----------|------|
| English | `eng` |

## Testing

Run the test suite:
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_ocr.py

# Run with verbose output
pytest -v
```

## Error Handling

The API provides detailed error responses:

```json
{
  "success": false,
  "error_code": "IMAGE_DOWNLOAD_ERROR",
  "error_message": "Failed to download image from URL",
  "details": {
    "url": "https://invalid-url.com/image.jpg",
    "status_code": 404
  }
}
```

### Common Error Codes

- `IMAGE_DOWNLOAD_ERROR`: Failed to download image from URL
- `INVALID_IMAGE_FORMAT`: Unsupported image format
- `IMAGE_TOO_LARGE`: Image exceeds maximum size limit
- `OCR_PROCESSING_ERROR`: OCR processing failed
- `VALIDATION_ERROR`: Request validation failed

## Performance Considerations

- **Image Size**: Larger images take longer to process. Consider resizing images before processing.
- **Preprocessing**: Image preprocessing improves accuracy but increases processing time.
- **Confidence Threshold**: Higher thresholds filter out low-confidence text but may miss valid text.
- **Language**: Specifying the correct language improves accuracy and performance.

## Security Notes

- The API downloads images from URLs, which may pose security risks in production.
- Consider implementing rate limiting and authentication for production use.
- Validate and sanitize image URLs to prevent SSRF attacks.
- Set appropriate resource limits to prevent DoS attacks.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## License

This project is licensed under the MIT License.

## Troubleshooting

### Common Issues

1. **EasyOCR installation issues**
   - Ensure you have sufficient disk space (EasyOCR downloads models automatically)
   - Check internet connectivity for first-time model download

2. **Image download failures**
   - Check internet connectivity
   - Verify image URL is accessible
   - Check if image URL requires authentication

3. **Low OCR accuracy**
   - Enable image preprocessing
   - Ensure image quality is sufficient
   - Try different image formats

4. **Memory issues**
   - Reduce maximum image size
   - Disable GPU if running out of GPU memory
   - Monitor memory usage

5. **Slow processing**
   - Enable GPU acceleration if available (`USE_GPU=true`)
   - Reduce image size before processing
   - Consider preprocessing images for better quality

### Getting Help

- Check the API documentation at `/api/v1/docs`
- Review the test cases for usage examples
- Open an issue on GitHub for bug reports or feature requests 
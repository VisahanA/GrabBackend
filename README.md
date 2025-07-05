# OCR & Speech-to-Text API

A robust FastAPI-based API that extracts text from images using OCR and transcribes audio to text using Speech Recognition.

## Features

### OCR (Optical Character Recognition)
- 🔤 **English OCR support** - Specialized for English language text recognition
- 📸 **Multiple image formats** - Supports JPEG, PNG, BMP, TIFF, and WEBP formats
- 🎯 **Confidence scoring** - Returns confidence scores for extracted text blocks
- 📍 **Bounding box detection** - Provides precise location coordinates for each text block
- 🔧 **Image preprocessing** - Automatic image enhancement for better OCR accuracy
- 🌐 **URL-based processing** - Process images directly from URLs
- 📝 **Detailed metadata** - Returns image information and processing statistics

### Speech-to-Text
- 🎤 **Multiple English variants** - Supports US, UK, Australian, and Canadian English
- 🔊 **Multiple audio formats** - Supports WAV, MP3, M4A, FLAC, and OGG formats
- 🎯 **Confidence scoring** - Returns confidence scores for transcribed text
- ⏱️ **Word timestamps** - Optional word-level timing information
- 👥 **Speaker diarization** - Optional speaker identification
- 🔧 **Audio preprocessing** - Automatic audio enhancement for better transcription
- 🌐 **URL-based processing** - Process audio directly from URLs
- 📝 **Detailed metadata** - Returns audio information and processing statistics

### General Features
- 🧪 **Well-tested** - Comprehensive test suite with mocking
- 📚 **Auto-generated documentation** - Interactive API docs with Swagger UI
- 🚀 **Production ready** - Error handling, validation, and monitoring

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
│   │           ├── ocr.py      # OCR endpoints
│   │           └── speech_to_text.py  # Speech-to-Text endpoints
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py           # Application configuration
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── ocr.py              # OCR Pydantic schemas
│   │   └── speech_to_text.py   # Speech-to-Text Pydantic schemas
│   └── services/
│       ├── __init__.py
│       ├── ocr_service.py      # OCR business logic
│       └── speech_to_text_service.py  # Speech-to-Text business logic
├── tests/
│   ├── __init__.py
│   ├── test_ocr.py             # OCR test cases
│   └── test_speech_to_text.py  # Speech-to-Text test cases
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## Prerequisites

### System Requirements

- Python 3.8+
- **No additional system dependencies required!** EasyOCR and SpeechRecognition work out of the box.

### GPU Support (Optional)
For faster OCR processing, you can enable GPU acceleration if you have:
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
| `MAX_AUDIO_SIZE_MB` | `25` | Maximum audio size in MB |
| `DEFAULT_OCR_LANGUAGE` | `eng` | Default OCR language |
| `DEFAULT_STT_LANGUAGE` | `en-US` | Default Speech-to-Text language |
| `IMAGE_DOWNLOAD_TIMEOUT` | `30` | Image download timeout (seconds) |
| `AUDIO_DOWNLOAD_TIMEOUT` | `30` | Audio download timeout (seconds) |
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

### OCR Endpoints

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
      "confidence": 95.5
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

### Speech-to-Text Endpoints

#### `POST /api/v1/stt/transcribe`
Transcribe audio to text.

**Request Body:**
```json
{
  "audio_url": "https://example.com/audio.wav",
  "language": "en-US",
  "confidence_threshold": 60.0,
  "enable_word_timestamps": false,
  "enable_speaker_diarization": false
}
```

**Response:**
```json
{
  "success": true,
  "transcribed_text": "Hello world! This is a sample audio transcription.",
  "word_timestamps": [
    {
      "word": "Hello",
      "start_time": 0.0,
      "end_time": 0.5,
      "confidence": 95.5
    }
  ],
  "speaker_segments": [
    {
      "speaker_id": 1,
      "start_time": 0.0,
      "end_time": 2.5,
      "text": "Hello world! This is a sample audio transcription.",
      "confidence": 91.85
    }
  ],
  "total_confidence": 91.85,
  "processing_time_ms": 2500.5,
  "audio_info": {
    "duration": 2.5,
    "format": "WAV",
    "sample_rate": 16000,
    "channels": 1,
    "size_bytes": 204800
  },
  "language_detected": "en-US"
}
```

#### `GET /api/v1/stt/supported-languages`
Get list of supported Speech-to-Text languages.

#### `GET /api/v1/stt/supported-formats`
Get list of supported audio formats.

#### `GET /api/v1/stt/health`
Health check for Speech-to-Text service.

### Utility Endpoints

#### `GET /`
API information and links.

#### `GET /health`
Basic health check.

## Usage Examples

### Python with requests

#### OCR Example
```python
import requests

# Extract text from image
response = requests.post(
    "http://localhost:8000/api/v1/ocr/extract-text",
    json={
        "image_url": "https://example.com/sample-image.jpg",
        "language": "eng",
        "confidence_threshold": 60.0,
        "preprocess_image": True
    }
)

if response.status_code == 200:
    result = response.json()
    print(f"Extracted text: {result['extracted_text']}")
    print(f"Confidence: {result['total_confidence']}%")
else:
    print(f"Error: {response.json()}")
```

#### Speech-to-Text Example
```python
import requests

# Transcribe audio to text
response = requests.post(
    "http://localhost:8000/api/v1/stt/transcribe",
    json={
        "audio_url": "https://example.com/sample-audio.wav",
        "language": "en-US",
        "confidence_threshold": 60.0,
        "enable_word_timestamps": True,
        "enable_speaker_diarization": False
    }
)

if response.status_code == 200:
    result = response.json()
    print(f"Transcribed text: {result['transcribed_text']}")
    print(f"Confidence: {result['total_confidence']}%")
    
    if result['word_timestamps']:
        for word in result['word_timestamps']:
            print(f"'{word['word']}' at {word['start_time']}-{word['end_time']}s")
else:
    print(f"Error: {response.json()}")
```

### cURL Examples

#### OCR
```bash
curl -X POST "http://localhost:8000/api/v1/ocr/extract-text" \
  -H "Content-Type: application/json" \
  -d '{
    "image_url": "https://example.com/sample-image.jpg",
    "language": "eng",
    "confidence_threshold": 60.0,
    "preprocess_image": true
  }'
```

#### Speech-to-Text
```bash
curl -X POST "http://localhost:8000/api/v1/stt/transcribe" \
  -H "Content-Type: application/json" \
  -d '{
    "audio_url": "https://example.com/sample-audio.wav",
    "language": "en-US",
    "confidence_threshold": 60.0,
    "enable_word_timestamps": true,
    "enable_speaker_diarization": false
  }'
```

## Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run specific test files
pytest tests/test_ocr.py
pytest tests/test_speech_to_text.py

# Run with coverage
pytest --cov=app tests/
```

## Error Handling

The API provides comprehensive error handling with specific error codes:

### OCR Errors
- `IMAGE_DOWNLOAD_ERROR` - Failed to download image
- `INVALID_IMAGE_FORMAT` - Unsupported image format
- `IMAGE_TOO_LARGE` - Image exceeds size limit
- `OCR_PROCESSING_ERROR` - OCR processing failed

### Speech-to-Text Errors
- `AUDIO_DOWNLOAD_ERROR` - Failed to download audio
- `INVALID_AUDIO_FORMAT` - Unsupported audio format
- `AUDIO_TOO_LARGE` - Audio exceeds size limit
- `SPEECH_RECOGNITION_ERROR` - Speech recognition failed

## Performance Considerations

### OCR Performance
- **CPU Processing**: ~1-3 seconds per image (depending on size and complexity)
- **GPU Processing**: ~0.5-1.5 seconds per image (with CUDA support)
- **Memory Usage**: ~200-500MB per request

### Speech-to-Text Performance
- **Processing Time**: ~1-5 seconds per minute of audio
- **Memory Usage**: ~100-300MB per request
- **Network Dependency**: Requires internet connection for Google Speech Recognition

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [EasyOCR](https://github.com/JaidedAI/EasyOCR) - For OCR functionality
- [SpeechRecognition](https://github.com/Uberi/speech_recognition) - For speech-to-text functionality
- [FastAPI](https://fastapi.tiangolo.com/) - For the web framework
- [Pydantic](https://pydantic-docs.helpmanual.io/) - For data validation 
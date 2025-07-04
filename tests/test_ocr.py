"""
Test cases for OCR API
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
from PIL import Image

from app.main import app
from app.schemas.ocr import OCRRequest, OCRResponse, OCRLanguage

client = TestClient(app)


class TestOCRAPI:
    """Test cases for OCR API endpoints"""
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "OCR API"
    
    def test_ocr_health_check(self):
        """Test OCR-specific health check endpoint"""
        response = client.get("/api/v1/ocr/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["service"] == "OCR API"
        assert data["ocr_engine"] == "EasyOCR"
    
    def test_supported_languages(self):
        """Test supported languages endpoint"""
        response = client.get("/api/v1/ocr/supported-languages")
        assert response.status_code == 200
        data = response.json()
        assert "supported_languages" in data
        assert "default_language" in data
        assert data["default_language"] == "eng"
        assert "English" in data["supported_languages"].values()
    
    def test_root_endpoint(self):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "OCR API"
        assert data["version"] == "1.0.0"
        assert "docs_url" in data
    
    @patch('app.services.ocr_service.OCRService.download_image')
    @patch('app.services.ocr_service.OCRService.extract_text_with_confidence')
    def test_extract_text_success(self, mock_extract, mock_download):
        """Test successful text extraction"""
        # Mock image
        mock_image = Mock(spec=Image.Image)
        mock_image.width = 800
        mock_image.height = 600
        mock_image.format = "JPEG"
        mock_image.mode = "RGB"
        mock_image.tobytes.return_value = b"fake_image_data"
        
        mock_download.return_value = mock_image
        
        # Mock OCR result
        mock_extract.return_value = {
            'text_blocks': [],
            'full_text': 'Hello World',
            'total_confidence': 95.0
        }
        
        # Test request
        request_data = {
            "image_url": "https://example.com/test.jpg",
            "language": "eng",
            "confidence_threshold": 0.0,
            "preprocess_image": True
        }
        
        response = client.post("/api/v1/ocr/extract-text", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert data["extracted_text"] == "Hello World"
        assert data["total_confidence"] == 95.0
    
    def test_extract_text_invalid_url(self):
        """Test text extraction with invalid URL"""
        request_data = {
            "image_url": "invalid-url",
            "language": "eng"
        }
        
        response = client.post("/api/v1/ocr/extract-text", json=request_data)
        assert response.status_code == 422  # Validation error
        
    def test_extract_text_missing_url(self):
        """Test text extraction without image URL"""
        request_data = {
            "language": "eng"
        }
        
        response = client.post("/api/v1/ocr/extract-text", json=request_data)
        assert response.status_code == 422  # Validation error
    
    def test_extract_text_invalid_language(self):
        """Test text extraction with invalid language"""
        request_data = {
            "image_url": "https://example.com/test.jpg",
            "language": "invalid_lang"
        }
        
        response = client.post("/api/v1/ocr/extract-text", json=request_data)
        assert response.status_code == 422  # Validation error
    
    def test_extract_text_invalid_confidence(self):
        """Test text extraction with invalid confidence threshold"""
        request_data = {
            "image_url": "https://example.com/test.jpg",
            "language": "eng",
            "confidence_threshold": 150.0  # Invalid: > 100
        }
        
        response = client.post("/api/v1/ocr/extract-text", json=request_data)
        assert response.status_code == 422  # Validation error
    
    @patch('app.services.ocr_service.OCRService.download_image')
    def test_extract_text_download_error(self, mock_download):
        """Test text extraction with download error"""
        mock_download.side_effect = Exception("IMAGE_DOWNLOAD_ERROR: Failed to download image")
        
        request_data = {
            "image_url": "https://example.com/nonexistent.jpg",
            "language": "eng"
        }
        
        response = client.post("/api/v1/ocr/extract-text", json=request_data)
        assert response.status_code == 400  # Bad request
        
        data = response.json()
        assert data["detail"]["success"] is False
        assert data["detail"]["error_code"] == "IMAGE_DOWNLOAD_ERROR"


class TestOCRService:
    """Test cases for OCR service functionality"""
    
    def test_ocr_request_schema(self):
        """Test OCR request schema validation"""
        # Valid request
        request = OCRRequest(
            image_url="https://example.com/image.jpg",
            language=OCRLanguage.ENGLISH,
            confidence_threshold=50.0,
            preprocess_image=True
        )
        
        assert str(request.image_url) == "https://example.com/image.jpg"
        assert request.language == OCRLanguage.ENGLISH
        assert request.confidence_threshold == 50.0
        assert request.preprocess_image is True
    
    def test_ocr_request_defaults(self):
        """Test OCR request schema with default values"""
        request = OCRRequest(image_url="https://example.com/image.jpg")
        
        assert request.language == OCRLanguage.ENGLISH
        assert request.confidence_threshold == 0.0
        assert request.preprocess_image is True
    
    def test_ocr_response_schema(self):
        """Test OCR response schema"""
        response = OCRResponse(
            success=True,
            extracted_text="Hello World",
            text_blocks=[],
            total_confidence=95.0,
            processing_time_ms=1000.0,
            image_info={"width": 800, "height": 600, "format": "JPEG"},
            language_detected="eng"
        )
        
        assert response.success is True
        assert response.extracted_text == "Hello World"
        assert response.total_confidence == 95.0
        assert response.processing_time_ms == 1000.0


if __name__ == "__main__":
    pytest.main([__file__]) 
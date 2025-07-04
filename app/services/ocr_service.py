import io
import time
import requests
import easyocr
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
from typing import Dict, List, Tuple
import tempfile
import os
from urllib.parse import urlparse

# Fix for PIL.Image.ANTIALIAS compatibility issue
if not hasattr(Image, 'ANTIALIAS'):
    Image.ANTIALIAS = Image.LANCZOS

from app.schemas.ocr import OCRRequest, OCRResponse, TextBlock, ErrorResponse
from app.core.config import settings


class OCRService:
    """Service class for handling OCR operations using EasyOCR"""
    
    def __init__(self):
        # Initialize EasyOCR reader for English only
        self.reader = easyocr.Reader(['en'], gpu=settings.USE_GPU)
        
        self.supported_formats = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif', '.webp'}
        self.max_image_size = settings.MAX_IMAGE_SIZE_MB * 1024 * 1024  # Convert to bytes
        self.download_timeout = settings.IMAGE_DOWNLOAD_TIMEOUT
        
    def download_image(self, image_url: str) -> Image.Image:
        """Download image from URL and return PIL Image object"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(str(image_url), headers=headers, timeout=self.download_timeout)
            response.raise_for_status()
            
            # Check content length
            if len(response.content) > self.max_image_size:
                raise ValueError(f"Image size ({len(response.content)} bytes) exceeds maximum allowed size ({self.max_image_size} bytes)")
            
            # Check if it's actually an image
            content_type = response.headers.get('content-type', '').lower()
            if not content_type.startswith('image/'):
                raise ValueError(f"URL does not point to an image (content-type: {content_type})")
            
            # Open image
            image = Image.open(io.BytesIO(response.content))
            return image
            
        except requests.RequestException as e:
            raise ValueError(f"Failed to download image: {str(e)}")
        except Exception as e:
            raise ValueError(f"Failed to process image: {str(e)}")
    
    def preprocess_image(self, image: Image.Image) -> Image.Image:
        """Preprocess image for better OCR results"""
        try:
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Resize if image is too large (keep aspect ratio)
            max_dimension = 2000
            if max(image.size) > max_dimension:
                ratio = max_dimension / max(image.size)
                new_size = tuple(int(dim * ratio) for dim in image.size)
                # Use LANCZOS instead of ANTIALIAS (which is deprecated)
                try:
                    image = image.resize(new_size, Image.Resampling.LANCZOS)
                except AttributeError:
                    # Fallback for older PIL versions
                    image = image.resize(new_size, Image.LANCZOS)
            
            # Enhance contrast
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(1.2)
            
            # Enhance sharpness
            enhancer = ImageEnhance.Sharpness(image)
            image = enhancer.enhance(1.1)
            
            # Apply slight noise reduction
            image = image.filter(ImageFilter.MedianFilter())
            
            return image
            
        except Exception as e:
            raise ValueError(f"Failed to preprocess image: {str(e)}")
    
    def extract_text_with_confidence(self, image: Image.Image, language: str) -> Dict:
        """Extract text with confidence scores using EasyOCR"""
        try:
            # Convert PIL Image to numpy array for EasyOCR
            image_array = np.array(image)
            
            # Use EasyOCR to extract text
            results = self.reader.readtext(image_array)
            
            # Extract text blocks
            text_blocks = []
            full_text_parts = []
            confidences = []
            
            for (bbox, text, confidence) in results:
                if text.strip() and confidence > 0:  # Only include text with positive confidence
                    # Convert bounding box from 4 points to x, y, width, height
                    bbox_points = np.array(bbox)
                    x_min = int(np.min(bbox_points[:, 0]))
                    y_min = int(np.min(bbox_points[:, 1]))
                    x_max = int(np.max(bbox_points[:, 0]))
                    y_max = int(np.max(bbox_points[:, 1]))
                    
                    text_block = TextBlock(
                        text=text.strip(),
                        confidence=float(confidence * 100),  # Convert to percentage (0-100)
                        bounding_box={
                            'x': x_min,
                            'y': y_min,
                            'width': x_max - x_min,
                            'height': y_max - y_min
                        }
                    )
                    text_blocks.append(text_block)
                    full_text_parts.append(text.strip())
                    confidences.append(confidence * 100)  # Convert to percentage
            
            # Calculate overall confidence
            total_confidence = sum(confidences) / len(confidences) if confidences else 0.0
            
            # Join all text
            full_text = ' '.join(full_text_parts)
            
            return {
                'text_blocks': text_blocks,
                'full_text': full_text,
                'total_confidence': total_confidence
            }
            
        except Exception as e:
            raise ValueError(f"OCR extraction failed: {str(e)}")
    
    def get_image_info(self, image: Image.Image) -> Dict:
        """Get image information"""
        return {
            'width': image.width,
            'height': image.height,
            'format': image.format or 'Unknown',
            'mode': image.mode,
            'size_bytes': len(image.tobytes()) if hasattr(image, 'tobytes') else 0
        }
    
    def detect_language(self, image: Image.Image) -> str:
        """Since we only support English, always return English"""
        return "eng"
    
    async def process_ocr_request(self, request: OCRRequest) -> OCRResponse:
        """Main method to process OCR request"""
        start_time = time.time()
        
        try:
            # Download image
            image = self.download_image(str(request.image_url))
            
            # Get original image info
            image_info = self.get_image_info(image)
            
            # Preprocess image if requested
            if request.preprocess_image:
                image = self.preprocess_image(image)
            
            # Since we only support English, set detected language to English
            detected_language = "eng"
            
            # Extract text with confidence
            ocr_result = self.extract_text_with_confidence(image, request.language.value)
            
            # Filter text blocks by confidence threshold
            filtered_blocks = [
                block for block in ocr_result['text_blocks'] 
                if block.confidence >= request.confidence_threshold
            ]
            
            # Recalculate full text from filtered blocks
            if request.confidence_threshold > 0:
                filtered_text = ' '.join([block.text for block in filtered_blocks])
                # Recalculate confidence for filtered blocks
                filtered_confidences = [block.confidence for block in filtered_blocks]
                total_confidence = sum(filtered_confidences) / len(filtered_confidences) if filtered_confidences else 0.0
            else:
                filtered_text = ocr_result['full_text']
                total_confidence = ocr_result['total_confidence']
                filtered_blocks = ocr_result['text_blocks']
            
            # Calculate processing time
            processing_time = (time.time() - start_time) * 1000
            
            return OCRResponse(
                success=True,
                extracted_text=filtered_text,
                text_blocks=filtered_blocks,
                total_confidence=total_confidence,
                processing_time_ms=processing_time,
                image_info=image_info,
                language_detected=detected_language
            )
            
        except Exception as e:
            # Return error response
            processing_time = (time.time() - start_time) * 1000
            error_message = str(e)
            
            # Determine error code based on error type
            if "download" in error_message.lower():
                error_code = "IMAGE_DOWNLOAD_ERROR"
            elif "format" in error_message.lower() or "image" in error_message.lower():
                error_code = "INVALID_IMAGE_FORMAT"
            elif "size" in error_message.lower():
                error_code = "IMAGE_TOO_LARGE"
            elif "ocr" in error_message.lower():
                error_code = "OCR_PROCESSING_ERROR"
            else:
                error_code = "UNKNOWN_ERROR"
            
            # For error responses, we need to return an ErrorResponse, but the endpoint expects OCRResponse
            # So we'll raise the exception and handle it in the FastAPI endpoint
            raise Exception(f"{error_code}: {error_message}")


# Global OCR service instance
ocr_service = OCRService() 
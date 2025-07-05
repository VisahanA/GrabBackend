import io
import time
import requests
import speech_recognition as sr
from pydub import AudioSegment
import tempfile
import os
import threading
from typing import Dict, List, Tuple, Optional
from urllib.parse import urlparse
from fastapi import UploadFile

from app.schemas.speech_to_text import STTRequest, STTResponse, STTFileRequest
from app.core.config import settings


# Set paths to your local ffmpeg/ffprobe binaries
os.environ["FFMPEG_BINARY"] = r"C:\ffmpeg-2025-06-28-git-cfd1f81e7d-essentials_build\bin" #"/path/to/ffmpeg"
os.environ["FFPROBE_BINARY"] = r"C:\ffmpeg-2025-06-28-git-cfd1f81e7d-essentials_build\bin" #"/path/to/ffprobe"

from pydub.utils import which
print("FFmpeg:", which("ffmpeg"))
print("FFprobe:", which("ffprobe"))


class TempFileManager:
    """Context manager for handling temporary files with proper cleanup on Windows"""
    
    def __init__(self, suffix='.wav'):
        self.temp_file_path = None
        self.suffix = suffix
    
    def __enter__(self):
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=self.suffix)
        self.temp_file_path = temp_file.name
        return temp_file
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.temp_file_path and os.path.exists(self.temp_file_path):
            print(f"TempFileManager: Preserving temporary file at: {self.temp_file_path}")
            # Don't delete the file - keep it for inspection/reuse


class SpeechToTextService:
    """Service class for handling Speech-to-Text operations using SpeechRecognition"""
    
    def __init__(self):
        # Initialize SpeechRecognition recognizer
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 300
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8
        
        self.supported_formats = {'.wav', '.mp3', '.m4a', '.flac', '.ogg'}
        self.max_audio_size = settings.MAX_AUDIO_SIZE_MB * 1024 * 1024  # Convert to bytes
        self.download_timeout = settings.AUDIO_DOWNLOAD_TIMEOUT
        
    def save_uploaded_file_to_temp(self, file: UploadFile) -> str:
        """Save uploaded file to temporary location and return file path"""
        try:
            # Validate file size
            file_content = file.file.read()
            if len(file_content) > self.max_audio_size:
                raise ValueError(f"Audio size ({len(file_content)} bytes) exceeds maximum allowed size ({self.max_audio_size} bytes)")
            
            # Get file extension
            file_extension = self._get_file_extension_from_filename(file.filename or "audio.wav")
            
            # Validate file extension
            if file_extension not in self.supported_formats:
                raise ValueError(f"Unsupported audio format: {file_extension}. Supported formats: {', '.join(self.supported_formats)}")
            
            # Create temporary file with proper extension
            with TempFileManager(suffix=file_extension) as temp_file:
                print(f"Writing uploaded audio to temporary file: {temp_file.name}")
                temp_file.write(file_content)
                temp_file_path = temp_file.name
                
                print(f"Audio saved to temporary location: {temp_file_path}")
                print(f"File size: {len(file_content)} bytes")
                
                return temp_file_path
            
        except Exception as e:
            raise ValueError(f"Failed to save uploaded audio file: {str(e)}")
    
    def _get_file_extension_from_filename(self, filename: str) -> str:
        """Get file extension from filename"""
        if not filename:
            return '.wav'
        
        # Get extension and ensure it has a dot
        ext = os.path.splitext(filename.lower())[1]
        if not ext:
            return '.wav'
        
        return ext
    
    def download_audio_to_temp(self, audio_url: str) -> str:
        """Download audio from HTTPS URL to temporary location and return file path"""
        try:
            # Validate URL
            parsed_url = urlparse(audio_url)
            if not parsed_url.scheme in ['http', 'https']:
                raise ValueError(f"Invalid URL scheme: {parsed_url.scheme}. Only HTTP/HTTPS URLs are supported.")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            print(f"Downloading audio from: {audio_url}")
            response = requests.get(str(audio_url), headers=headers, timeout=self.download_timeout)
            response.raise_for_status()
            
            # Check content length
            if len(response.content) > self.max_audio_size:
                raise ValueError(f"Audio size ({len(response.content)} bytes) exceeds maximum allowed size ({self.max_audio_size} bytes)")
            
            # Check if it's actually an audio file
            content_type = response.headers.get('content-type', '').lower()
            if not any(audio_type in content_type for audio_type in ['audio/', 'application/octet-stream', 'video/']):
                print(f"Warning: Content-Type is {content_type}, but proceeding anyway...")
            
            # Determine file extension from URL or content-type
            file_extension = self._get_file_extension(audio_url, content_type)
            
            # Create temporary file with proper extension
            with TempFileManager(suffix=file_extension) as temp_file:
                print(f"Writing audio to temporary file: {temp_file.name}")
                temp_file.write(response.content)
                temp_file_path = temp_file.name
                
                print(f"Audio downloaded to temporary location: {temp_file_path}")
                print(f"File size: {len(response.content)} bytes")
                
                return temp_file_path
            
        except requests.RequestException as e:
            raise ValueError(f"Failed to download audio from {audio_url}: {str(e)}")
        except Exception as e:
            raise ValueError(f"Failed to process audio from {audio_url}: {str(e)}")
    
    def _get_file_extension(self, audio_url: str, content_type: str) -> str:
        """Determine the appropriate file extension based on URL and content type"""
        # Try to get extension from URL
        url_path = urlparse(audio_url).path.lower()
        if url_path.endswith(('.wav', '.mp3', '.m4a', '.flac', '.ogg', '.aac')):
            return os.path.splitext(url_path)[1]
        
        # Try to get extension from content type
        content_type_mapping = {
            'audio/wav': '.wav',
            'audio/mpeg': '.mp3',
            'audio/mp4': '.m4a',
            'audio/flac': '.flac',
            'audio/ogg': '.ogg',
            'audio/aac': '.aac',
            'application/octet-stream': '.wav',  # Default fallback
        }
        
        for audio_type, extension in content_type_mapping.items():
            if audio_type in content_type:
                return extension
        
        # Default fallback
        return '.wav'
    
    def load_audio_from_temp(self, temp_file_path: str) -> AudioSegment:
        """Load audio from temporary file location"""
        try:
            print(f"Line 131 - Loading audio from temporary file: {temp_file_path}")
            
            # Try to load with auto-detection first
            try:
                audio = AudioSegment.from_file(temp_file_path)
            except Exception as e:
                # Try with specific formats
                for format_name in ['wav', 'mp3', 'm4a', 'flac', 'ogg']:
                    try:
                        audio = AudioSegment.from_file(temp_file_path, format=format_name)
                        print(f"Line 141Successfully loaded audio as {format_name}")
                        break
                    except:
                        continue
                else:
                    raise ValueError(f"Unsupported audio format. Error: {str(e)}")
            
            print(f"Audio loaded successfully. Duration: {len(audio)/1000:.2f} seconds")
            return audio
            
        except Exception as e:
            raise ValueError(f"Failed to load audio from temporary file: {str(e)}")
    
    def download_audio(self, audio_url: str) -> AudioSegment:
        """Download audio from URL and return AudioSegment object (legacy method)"""
        temp_file_path = self.download_audio_to_temp(audio_url)
        return self.load_audio_from_temp(temp_file_path)
    
    def preprocess_audio(self, audio: AudioSegment) -> AudioSegment:
        """Preprocess audio for better transcription results"""
        try:
            # Convert to mono if stereo
            if audio.channels > 1:
                audio = audio.set_channels(1)
            
            # Set sample rate to 16kHz (optimal for speech recognition)
            if audio.frame_rate != 16000:
                audio = audio.set_frame_rate(16000)
            
            # Normalize audio
            audio = audio.normalize()
            
            # Apply noise reduction (simple approach)
            # In production, you might want to use more sophisticated noise reduction
            
            return audio
            
        except Exception as e:
            raise ValueError(f"Failed to preprocess audio: {str(e)}")
    
    def extract_text_with_confidence(self, audio: AudioSegment) -> Dict:
        """Extract text with confidence scores using SpeechRecognition"""
        try:
            # Convert AudioSegment to bytes for SpeechRecognition
            audio_bytes = io.BytesIO()
            audio.export(audio_bytes, format="wav")
            audio_bytes.seek(0)
            
            # Create AudioData object for SpeechRecognition
            audio_data = sr.AudioData(
                audio_bytes.read(),
                audio.frame_rate,
                audio.sample_width
            )
            
            # Clear the BytesIO buffer to free memory
            audio_bytes.close()
            
            # Use SpeechRecognition to extract text
            # Note: SpeechRecognition doesn't provide confidence scores by default
            # We'll use Google's speech recognition which provides confidence
            try:
                result = self.recognizer.recognize_google(
                    audio_data,
                    language="en-US",  # English only
                    show_all=True  # This returns multiple alternatives with confidence
                )
                
                if not result or 'alternative' not in result:
                    raise ValueError("No speech detected in audio")
                
                # Get the best alternative
                best_alternative = result['alternative'][0]
                transcribed_text = best_alternative.get('transcript', '')
                
                # Calculate confidence (Google doesn't always provide this)
                confidence = best_alternative.get('confidence', 0.8) * 100
                
                return {
                    'transcribed_text': transcribed_text,
                    'confidence': confidence
                }
                
            except sr.UnknownValueError:
                raise ValueError("Speech could not be understood")
            except sr.RequestError as e:
                raise ValueError(f"Speech recognition service error: {str(e)}")
            
        except Exception as e:
            raise ValueError(f"Speech recognition failed: {str(e)}")
    
    def get_audio_info(self, audio: AudioSegment) -> Dict:
        """Get audio information"""
        return {
            'duration': len(audio) / 1000.0,  # Duration in seconds
            'format': 'WAV',  # We convert to WAV for processing
            'sample_rate': audio.frame_rate,
            'channels': audio.channels,
            'size_bytes': len(audio.raw_data) if hasattr(audio, 'raw_data') else 0
        }
    
    async def process_uploaded_file_request(self, file: UploadFile, request: STTFileRequest) -> STTResponse:
        """Process Speech-to-Text request with uploaded file"""
        start_time = time.time()
        temp_file_path = None
        
        try:
            # Step 1: Save uploaded file to temporary location
            print(f"Processing STT request for uploaded file: {file.filename}")
            temp_file_path = self.save_uploaded_file_to_temp(file)
            
            # Step 2: Load audio from temporary location
            audio = self.load_audio_from_temp(temp_file_path)
            
            # Get original audio info
            audio_info = self.get_audio_info(audio)
            
            # Preprocess audio
            audio = self.preprocess_audio(audio)
            
            # Extract text with confidence
            stt_result = self.extract_text_with_confidence(audio)
            
            # Filter by confidence threshold if needed
            if request.confidence_threshold > 0 and stt_result['confidence'] < request.confidence_threshold:
                # If overall confidence is below threshold, return empty result
                transcribed_text = ""
                total_confidence = 0.0
            else:
                transcribed_text = stt_result['transcribed_text']
                total_confidence = stt_result['confidence']
            
            # Pass transcribed text to LLM service for processing
            if transcribed_text:
                from app.services.llm_service import LLMService
                from app.schemas.llm import LLMRequest
                
                llm_service = LLMService()
                llm_request = LLMRequest(prompt=transcribed_text)
                llm_response = llm_service.generate_text(llm_request)
                
                # Use LLM response as the final transcribed text
                final_text = llm_response.generated_text
            else:
                final_text = ""
            
            # Calculate processing time
            processing_time = (time.time() - start_time) * 1000
            
            return STTResponse(
                success=True,
                transcribed_text=final_text,
                total_confidence=total_confidence,
                processing_time_ms=processing_time,
                audio_info=audio_info
            )
            
        except Exception as e:
            # Return error response
            processing_time = (time.time() - start_time) * 1000
            error_message = str(e)
            
            # Keep temporary file for inspection/reuse
            if temp_file_path and os.path.exists(temp_file_path):
                print(f"Temporary audio file preserved at: {temp_file_path}")
            
            # Determine error code based on error type
            if "save" in error_message.lower() or "upload" in error_message.lower():
                error_code = "AUDIO_UPLOAD_ERROR"
            elif "format" in error_message.lower() or "audio" in error_message.lower():
                error_code = "INVALID_AUDIO_FORMAT"
            elif "size" in error_message.lower():
                error_code = "AUDIO_TOO_LARGE"
            elif "speech" in error_message.lower():
                error_code = "SPEECH_RECOGNITION_ERROR"
            else:
                error_code = "UNKNOWN_ERROR"
            
            # Raise exception to be handled by the FastAPI endpoint
            raise Exception(f"{error_code}: {error_message}")
        finally:
            # Keep temporary files for inspection/reuse
            if temp_file_path and os.path.exists(temp_file_path):
                print(f"Temporary audio file preserved at: {temp_file_path}")
    
    async def process_stt_request(self, request: STTRequest) -> STTResponse:
        """Main method to process Speech-to-Text request"""
        start_time = time.time()
        temp_file_path = None
        
        try:
            # Step 1: Download audio from HTTPS URL to temporary location
            print(f"Processing STT request for URL: {request.audio_url}")
            temp_file_path = self.download_audio_to_temp(str(request.audio_url))
            #temp_file_path = r"C:\Users\sreenila\AppData\Local\Temp\tmpas2w37ky.wav"
            
            # Step 2: Load audio from temporary location
            audio = self.load_audio_from_temp(temp_file_path)
            
            # Get original audio info
            audio_info = self.get_audio_info(audio)
            
            # Preprocess audio
            audio = self.preprocess_audio(audio)
            
            # Extract text with confidence
            stt_result = self.extract_text_with_confidence(
                audio
            )
            
            # Filter by confidence threshold if needed
            if request.confidence_threshold > 0 and stt_result['confidence'] < request.confidence_threshold:
                # If overall confidence is below threshold, return empty result
                transcribed_text = ""
                total_confidence = 0.0
            else:
                transcribed_text = stt_result['transcribed_text']
                total_confidence = stt_result['confidence']
            
            # Pass transcribed text to LLM service for processing
            if transcribed_text:
                from app.services.llm_service import LLMService
                from app.schemas.llm import LLMRequest
                
                llm_service = LLMService()
                llm_request = LLMRequest(prompt=transcribed_text)
                llm_response = llm_service.generate_text(llm_request)
                print(f"LLM response: {llm_response}")
                
                # Use LLM response as the final transcribed text
                final_text = llm_response.generated_text
            else:
                final_text = ""
            
            # Calculate processing time
            processing_time = (time.time() - start_time) * 1000
            
            return STTResponse(
                success=True,
                transcribed_text=final_text,
                total_confidence=total_confidence,
                processing_time_ms=processing_time,
                audio_info=audio_info
            )
            
        except Exception as e:
            # Return error response
            processing_time = (time.time() - start_time) * 1000
            error_message = str(e)
            
            # Keep temporary file for inspection/reuse
            if temp_file_path and os.path.exists(temp_file_path):
                print(f"Temporary audio file preserved at: {temp_file_path}")
            
            # Determine error code based on error type
            if "download" in error_message.lower():
                error_code = "AUDIO_DOWNLOAD_ERROR"
            elif "format" in error_message.lower() or "audio" in error_message.lower():
                error_code = "INVALID_AUDIO_FORMAT"
            elif "size" in error_message.lower():
                error_code = "AUDIO_TOO_LARGE"
            elif "speech" in error_message.lower():
                error_code = "SPEECH_RECOGNITION_ERROR"
            else:
                error_code = "UNKNOWN_ERROR"
            
            # Raise exception to be handled by the FastAPI endpoint
            raise Exception(f"{error_code}: {error_message}")
        finally:
            # Keep temporary files for inspection/reuse
            if temp_file_path and os.path.exists(temp_file_path):
                print(f"Temporary audio file preserved at: {temp_file_path}")


# Create service instance
stt_service = SpeechToTextService() 
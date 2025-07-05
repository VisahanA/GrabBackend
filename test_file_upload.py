#!/usr/bin/env python3
"""
Test script for the new audio file upload endpoint
"""

import requests
import os
from pathlib import Path

# Configuration
API_BASE_URL = "http://localhost:8000"
UPLOAD_ENDPOINT = f"{API_BASE_URL}/api/v1/stt/transcribe-file"

def test_file_upload(audio_file_path: str, confidence_threshold: float = 0.0):
    """
    Test the new file upload endpoint
    
    Args:
        audio_file_path: Path to the audio file to upload
        confidence_threshold: Minimum confidence threshold (0-100)
    """
    
    # Check if file exists
    if not os.path.exists(audio_file_path):
        print(f"❌ Audio file not found: {audio_file_path}")
        return False
    
    # Get file info
    file_size = os.path.getsize(audio_file_path)
    file_name = os.path.basename(audio_file_path)
    
    print(f"📁 Testing file upload for: {file_name}")
    print(f"📊 File size: {file_size:,} bytes ({file_size/1024/1024:.2f} MB)")
    print(f"🎯 Confidence threshold: {confidence_threshold}%")
    print("-" * 50)
    
    try:
        # Prepare the multipart form data
        with open(audio_file_path, 'rb') as audio_file:
            files = {
                'audio_file': (file_name, audio_file, 'audio/wav')
            }
            
            data = {
                'confidence_threshold': confidence_threshold
            }
            
            print("📤 Uploading file...")
            response = requests.post(
                UPLOAD_ENDPOINT,
                files=files,
                data=data,
                timeout=60  # 60 second timeout
            )
        
        print(f"📋 Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            print("✅ SUCCESS!")
            print(f"📝 Transcribed text: {result['transcribed_text']}")
            print(f"🎯 Confidence: {result['total_confidence']:.2f}%")
            print(f"⏱️ Processing time: {result['processing_time_ms']:.2f}ms")
            
            # Audio info
            audio_info = result['audio_info']
            print(f"🔊 Audio duration: {audio_info['duration']:.2f}s")
            print(f"🎵 Sample rate: {audio_info['sample_rate']} Hz")
            print(f"📢 Channels: {audio_info['channels']}")
            
            return True
            
        else:
            print("❌ ERROR!")
            try:
                error_detail = response.json()
                print(f"🚨 Error code: {error_detail['error_code']}")
                print(f"💬 Error message: {error_detail['error_message']}")
                
                if 'details' in error_detail:
                    print(f"📄 Details: {error_detail['details']}")
                    
            except:
                print(f"💬 Error response: {response.text}")
            
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out (60 seconds)")
        return False
        
    except requests.exceptions.ConnectionError:
        print("❌ Connection error - make sure the server is running on http://localhost:8000")
        return False
        
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False


def test_url_endpoint(audio_url: str, confidence_threshold: float = 0.0):
    """
    Test the existing URL-based endpoint for comparison
    
    Args:
        audio_url: URL of the audio file
        confidence_threshold: Minimum confidence threshold (0-100)
    """
    
    url_endpoint = f"{API_BASE_URL}/api/v1/stt/transcribe"
    
    print(f"🌐 Testing URL endpoint with: {audio_url}")
    print(f"🎯 Confidence threshold: {confidence_threshold}%")
    print("-" * 50)
    
    try:
        payload = {
            "audio_url": audio_url,
            "confidence_threshold": confidence_threshold
        }
        
        print("📤 Sending URL request...")
        response = requests.post(
            url_endpoint,
            json=payload,
            timeout=60
        )
        
        print(f"📋 Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            print("✅ SUCCESS!")
            print(f"📝 Transcribed text: {result['transcribed_text']}")
            print(f"🎯 Confidence: {result['total_confidence']:.2f}%")
            print(f"⏱️ Processing time: {result['processing_time_ms']:.2f}ms")
            
            return True
            
        else:
            print("❌ ERROR!")
            try:
                error_detail = response.json()
                print(f"🚨 Error code: {error_detail['error_code']}")
                print(f"💬 Error message: {error_detail['error_message']}")
                
            except:
                print(f"💬 Error response: {response.text}")
            
            return False
            
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False


def main():
    """
    Main test function
    """
    print("🎙️ Audio Transcription API Test")
    print("=" * 50)
    
    # Test file upload endpoint
    print("\n1️⃣ Testing FILE UPLOAD endpoint")
    print("=" * 30)
    
    # You can test with your own audio file
    test_audio_file = "test_audio.wav"  # Replace with your actual audio file path
    
    if os.path.exists(test_audio_file):
        test_file_upload(test_audio_file, confidence_threshold=60.0)
    else:
        print(f"⚠️ Test audio file not found: {test_audio_file}")
        print("   Please provide a valid audio file path to test the upload functionality.")
    
    # Test URL endpoint (this will fail with the localhost URL issue)
    print("\n2️⃣ Testing URL endpoint (for comparison)")
    print("=" * 30)
    
    # This will demonstrate the original problem
    test_url_endpoint("http://localhost:3000/uploads/audio_1751755409858.wav", confidence_threshold=60.0)
    
    print("\n" + "=" * 50)
    print("✨ Test completed!")
    print("\n📌 SOLUTION SUMMARY:")
    print("   - Use the NEW /api/v1/stt/transcribe-file endpoint for direct file uploads")
    print("   - Use the existing /api/v1/stt/transcribe endpoint for publicly accessible URLs")
    print("   - The file upload endpoint eliminates the need for a separate file server")


if __name__ == "__main__":
    main() 
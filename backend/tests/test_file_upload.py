#!/usr/bin/env python3
"""
Test script for file upload functionality
"""

import requests
import os
from pathlib import Path

def test_file_upload():
    """Test the file upload endpoint"""
    
    # Create a test PDF file (dummy content)
    test_pdf_content = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n>>\nendobj\nxref\n0 4\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \ntrailer\n<<\n/Size 4\n/Root 1 0 R\n>>\nstartxref\n174\n%%EOF"
    
    # Save test file
    test_file_path = "test_book.pdf"
    with open(test_file_path, "wb") as f:
        f.write(test_pdf_content)
    
    try:
        # Test file upload
        print("🧪 Testing file upload...")
        
        url = "http://localhost:8000/api/v1/upload/file"
        headers = {"X-User-ID": "test-user-123"}
        
        with open(test_file_path, "rb") as f:
            files = {"file": ("test_book.pdf", f, "application/pdf")}
            response = requests.post(url, headers=headers, files=files)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            file_data = response.json()
            file_id = file_data["fileId"]
            print(f"✅ File uploaded successfully with ID: {file_id}")
            
            # Test file download
            print("\n🧪 Testing file download...")
            download_url = f"http://localhost:8000/api/v1/files/{file_id}"
            download_response = requests.get(download_url)
            
            print(f"Download Status Code: {download_response.status_code}")
            if download_response.status_code == 200:
                print("✅ File downloaded successfully")
            else:
                print("❌ File download failed")
            
            # Test file listing
            print("\n🧪 Testing file listing...")
            list_url = "http://localhost:8000/api/v1/files"
            list_response = requests.get(list_url, headers=headers)
            
            print(f"List Status Code: {list_response.status_code}")
            print(f"List Response: {list_response.json()}")
            
            if list_response.status_code == 200:
                print("✅ File listing successful")
            else:
                print("❌ File listing failed")
        
        else:
            print("❌ File upload failed")
    
    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")
    
    finally:
        # Clean up test file
        if os.path.exists(test_file_path):
            os.remove(test_file_path)
            print(f"🧹 Cleaned up test file: {test_file_path}")

def test_chat_with_file():
    """Test chat endpoint with file attachment"""
    
    # Create a test PDF file
    test_pdf_content = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n>>\nendobj\nxref\n0 4\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \ntrailer\n<<\n/Size 4\n/Root 1 0 R\n>>\nstartxref\n174\n%%EOF"
    
    test_file_path = "test_physics_book.pdf"
    with open(test_file_path, "wb") as f:
        f.write(test_pdf_content)
    
    try:
        print("\n🧪 Testing chat with file attachment...")
        
        url = "http://localhost:8000/api/v1/chat/message"
        headers = {"X-User-ID": "test-user-123"}
        
        data = {
            "message": "Can you help me understand the concepts in this physics book?",
            "message_id": "msg-test-file",
            "user_id": "test-user-123",
            "timestamp": "2024-01-01T00:00:00Z",
            "require_audio": False
        }
        
        with open(test_file_path, "rb") as f:
            files = {"attached_file": ("test_physics_book.pdf", f, "application/pdf")}
            response = requests.post(url, headers=headers, data=data, files=files)
        
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            response_data = response.json()
            print("✅ Chat with file attachment successful")
            print(f"Response includes attached file: {response_data['responses'][0].get('attachedFile') is not None}")
        else:
            print("❌ Chat with file attachment failed")
            print(f"Response: {response.text}")
    
    except Exception as e:
        print(f"❌ Error during chat testing: {str(e)}")
    
    finally:
        # Clean up test file
        if os.path.exists(test_file_path):
            os.remove(test_file_path)
            print(f"🧹 Cleaned up test file: {test_file_path}")

if __name__ == "__main__":
    print("🚀 Starting file upload tests...")
    test_file_upload()
    test_chat_with_file()
    print("\n✅ All tests completed!")


import requests
import os
from pathlib import Path
import time

BASE_URL = "http://localhost:5000"

def test_server_status():
    """Test if the server is running."""
    print("\n🔍 Testing server status...")
    try:
        response = requests.get(f"{BASE_URL}/test")
        if response.status_code == 200:
            print("✅ Server is running!")
            print(f"Response: {response.json()}")
        else:
            print("❌ Server test failed!")
            print(f"Status code: {response.status_code}")
            print(f"Response: {response.text}")
    except requests.RequestException as e:
        print(f"❌ Error connecting to server: {str(e)}")

def test_pdf_upload(pdf_path):
    """Test PDF upload and processing."""
    print("\n🔍 Testing PDF upload...")
    
    if not os.path.exists(pdf_path):
        print(f"❌ PDF file not found at: {pdf_path}")
        return
    
    try:
        # Prepare the file for upload
        with open(pdf_path, 'rb') as f:
            files = {'file': (os.path.basename(pdf_path), f, 'application/pdf')}
            
            print("📤 Uploading PDF...")
            start_time = time.time()
            
            response = requests.post(f"{BASE_URL}/upload", files=files)
            
            processing_time = time.time() - start_time
            
            if response.status_code == 200:
                print(f"✅ PDF processed successfully! (took {processing_time:.2f} seconds)")
                result = response.json()
                
                # Print summary of results
                print("\n📊 Results Summary:")
                print("-------------------")
                
                if 'summary' in result:
                    print("\n📝 Summary:")
                    print(result['summary'][:500] + "..." if len(result['summary']) > 500 else result['summary'])
                
                if 'metadata' in result:
                    print("\n📋 Metadata:")
                    for key, value in result.get('metadata', {}).items():
                        print(f"  - {key}: {value}")
                
                if 'images' in result:
                    print(f"\n🖼 Images extracted: {len(result['images'])}")
                    for idx, image in enumerate(result['images']):
                        print(f"  - Image {idx + 1}: {image.get('path')}")
                        if image.get('caption'):
                            print(f"    Caption: {image['caption']}")
                
                if 'tables' in result:
                    print(f"\n📊 Tables extracted: {len(result['tables'])}")
                
                if 'document_structure' in result:
                    print("\n📑 Document Structure:")
                    structure = result['document_structure']
                    if 'key_concepts' in structure:
                        print("  Key concepts:", ", ".join(structure['key_concepts'][:5]))
                    if 'topics' in structure:
                        print("  Topics:", ", ".join(structure['topics'][:5]))
                
            else:
                print("❌ PDF processing failed!")
                print(f"Status code: {response.status_code}")
                print(f"Error: {response.json().get('error', 'Unknown error')}")
                
    except requests.RequestException as e:
        print(f"❌ Error during upload: {str(e)}")

def test_image_retrieval(image_path):
    """Test retrieving a processed image."""
    print("\n🔍 Testing image retrieval...")
    try:
        response = requests.get(f"{BASE_URL}/images/{os.path.basename(image_path)}")
        if response.status_code == 200:
            print("✅ Image retrieved successfully!")
            print(f"Size: {len(response.content)} bytes")
        else:
            print("❌ Image retrieval failed!")
            print(f"Status code: {response.status_code}")
            print(f"Response: {response.text}")
    except requests.RequestException as e:
        print(f"❌ Error retrieving image: {str(e)}")

def main():
    """Run all tests."""
    print("🚀 Starting API endpoint tests...")
    
    # Test server status
    test_server_status()
    
    # Test PDF upload with a sample PDF
    sample_pdf_path = "sample/sample.pdf"  # Replace with your PDF path
    test_pdf_upload(sample_pdf_path)
    
    # If we know an image was generated, test retrieving it
    # test_image_retrieval("image_0.png")
    
    print("\n✨ Testing complete!")

if __name__ == "__main__":
    main()
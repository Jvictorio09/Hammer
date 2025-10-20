#!/usr/bin/env python
"""
Test script for Google Drive upload functionality.
Run this to verify your setup before using the API endpoints.

Usage:
    python test_google_drive_upload.py
"""

import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myProject.settings')
django.setup()

from myApp.utils.google_drive_utils import (
    get_drive_service,
    extract_file_id_from_url,
    download_file_from_drive,
    upload_from_google_drive_to_cloudinary
)


def test_credentials():
    """Test if Google Drive credentials are properly configured."""
    print("=" * 60)
    print("Testing Google Drive Credentials")
    print("=" * 60)
    
    creds_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    if not creds_path:
        print("❌ GOOGLE_APPLICATION_CREDENTIALS not set in environment")
        print("   Add it to your .env file:")
        print("   GOOGLE_APPLICATION_CREDENTIALS=/path/to/google-credentials.json")
        return False
    
    print(f"✅ Credentials path set: {creds_path}")
    
    if not os.path.exists(creds_path):
        print(f"❌ Credentials file not found at: {creds_path}")
        return False
    
    print(f"✅ Credentials file exists")
    
    try:
        service = get_drive_service()
        print("✅ Google Drive service initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to initialize Drive service: {str(e)}")
        return False


def test_url_extraction():
    """Test URL parsing."""
    print("\n" + "=" * 60)
    print("Testing URL Extraction")
    print("=" * 60)
    
    test_urls = [
        ("https://drive.google.com/file/d/1ABC123xyz/view", "1ABC123xyz"),
        ("https://drive.google.com/open?id=1XYZ789abc", "1XYZ789abc"),
        ("1DirectFileID", "1DirectFileID"),
    ]
    
    all_passed = True
    for url, expected_id in test_urls:
        result = extract_file_id_from_url(url)
        if result == expected_id:
            print(f"✅ {url[:50]}... → {result}")
        else:
            print(f"❌ {url[:50]}... → Expected: {expected_id}, Got: {result}")
            all_passed = False
    
    return all_passed


def test_file_download():
    """Test downloading a file from Google Drive."""
    print("\n" + "=" * 60)
    print("Testing File Download")
    print("=" * 60)
    
    # Ask user for a test file
    print("\nTo test file download, you need a Google Drive file that:")
    print("  1. Is an image (JPEG, PNG, etc.)")
    print("  2. Is shared with your service account email")
    print("     (Find the email in your google-credentials.json)")
    print()
    
    file_url = input("Enter Google Drive file URL (or 'skip' to skip): ").strip()
    
    if file_url.lower() == 'skip':
        print("⏭️  Skipping file download test")
        return True
    
    try:
        file_id = extract_file_id_from_url(file_url)
        if not file_id:
            print("❌ Invalid file URL")
            return False
        
        print(f"📥 Downloading file: {file_id}")
        file_bytes, metadata = download_file_from_drive(file_id)
        
        print(f"✅ Downloaded successfully!")
        print(f"   Name: {metadata.get('name')}")
        print(f"   Type: {metadata.get('mimeType')}")
        print(f"   Size: {len(file_bytes):,} bytes")
        
        return True
    except Exception as e:
        print(f"❌ Download failed: {str(e)}")
        print("\n💡 Common issues:")
        print("   - File not shared with service account")
        print("   - Invalid file ID")
        print("   - File is not an image")
        return False


def test_full_upload():
    """Test full upload to Cloudinary."""
    print("\n" + "=" * 60)
    print("Testing Full Upload to Cloudinary")
    print("=" * 60)
    
    print("\n⚠️  This will upload an image to Cloudinary!")
    print("Make sure you have:")
    print("  1. Cloudinary credentials configured in .env")
    print("  2. A test image shared with your service account")
    print()
    
    proceed = input("Proceed with upload test? (yes/no): ").strip().lower()
    if proceed != 'yes':
        print("⏭️  Skipping upload test")
        return True
    
    file_url = input("Enter Google Drive file URL: ").strip()
    
    try:
        print("\n📤 Starting upload process...")
        result, web_url, thumb_url, metadata = upload_from_google_drive_to_cloudinary(
            drive_file_id_or_url=file_url,
            cloudinary_folder='test_uploads',
            tags=['test'],
            auto_compress=True
        )
        
        print(f"✅ Upload successful!")
        print(f"   Original: {metadata.get('name')} ({metadata.get('size')} bytes)")
        print(f"   Public ID: {result.get('public_id')}")
        print(f"   Web URL: {web_url}")
        print(f"   Uploaded: {result.get('bytes')} bytes")
        
        if int(metadata.get('size', 0)) > result.get('bytes', 0):
            print(f"   🎉 Compressed: {int(metadata.get('size', 0)) - result.get('bytes', 0):,} bytes saved!")
        
        return True
    except Exception as e:
        print(f"❌ Upload failed: {str(e)}")
        return False


def main():
    """Run all tests."""
    print("\n🚀 Google Drive Upload Test Suite\n")
    
    # Test 1: Credentials
    if not test_credentials():
        print("\n❌ Setup incomplete. Fix credentials first.")
        return
    
    # Test 2: URL Extraction
    test_url_extraction()
    
    # Test 3: File Download (optional)
    test_file_download()
    
    # Test 4: Full Upload (optional)
    test_full_upload()
    
    print("\n" + "=" * 60)
    print("✅ Testing Complete!")
    print("=" * 60)
    print("\nYou can now use the API endpoints:")
    print("  POST /dashboard/gallery/api/google-drive/upload/")
    print("  POST /dashboard/gallery/api/google-drive/bulk-upload/")
    print("\nSee GOOGLE_DRIVE_UPLOAD_SETUP.md for usage examples.")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()


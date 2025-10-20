# myApp/utils/google_drive_utils.py
import io
import os
from typing import Optional, Tuple, Dict, Any
from google.oauth2.credentials import Credentials
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.errors import HttpError
from django.conf import settings
from PIL import Image
from .cloudinary_utils import smart_compress_to_bytes, upload_to_cloudinary, TARGET_BYTES


def get_drive_service(credentials_json_path: Optional[str] = None):
    """
    Initialize and return a Google Drive API service instance.
    
    Args:
        credentials_json_path: Path to service account JSON file. 
                              If None, looks for GOOGLE_APPLICATION_CREDENTIALS env var.
    
    Returns:
        Google Drive service object
    """
    try:
        # Try to use service account credentials
        creds_path = credentials_json_path or os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        
        if creds_path and os.path.exists(creds_path):
            credentials = service_account.Credentials.from_service_account_file(
                creds_path,
                scopes=['https://www.googleapis.com/auth/drive.readonly']
            )
        else:
            raise ValueError(
                "Google Drive credentials not found. "
                "Set GOOGLE_APPLICATION_CREDENTIALS environment variable or provide credentials_json_path."
            )
        
        service = build('drive', 'v3', credentials=credentials)
        return service
    
    except Exception as e:
        raise Exception(f"Failed to initialize Google Drive service: {str(e)}")


def extract_file_id_from_url(drive_url: str) -> Optional[str]:
    """
    Extract file ID from various Google Drive URL formats.
    
    Supports:
    - https://drive.google.com/file/d/FILE_ID/view
    - https://drive.google.com/open?id=FILE_ID
    - https://drive.google.com/uc?id=FILE_ID
    - Direct FILE_ID
    
    Args:
        drive_url: Google Drive URL or file ID
        
    Returns:
        File ID string or None if not found
    """
    import re
    
    # If it's already just an ID (alphanumeric with hyphens and underscores)
    if re.match(r'^[a-zA-Z0-9_-]+$', drive_url):
        return drive_url
    
    # Pattern 1: /file/d/FILE_ID/
    match = re.search(r'/file/d/([a-zA-Z0-9_-]+)', drive_url)
    if match:
        return match.group(1)
    
    # Pattern 2: ?id=FILE_ID or &id=FILE_ID
    match = re.search(r'[?&]id=([a-zA-Z0-9_-]+)', drive_url)
    if match:
        return match.group(1)
    
    # Pattern 3: /folders/FILE_ID or /d/FILE_ID
    match = re.search(r'/(?:folders|d)/([a-zA-Z0-9_-]+)', drive_url)
    if match:
        return match.group(1)
    
    return None


def download_file_from_drive(
    file_id: str, 
    service=None,
    credentials_path: Optional[str] = None
) -> Tuple[bytes, Dict[str, Any]]:
    """
    Download a file from Google Drive and return its bytes content.
    
    Args:
        file_id: Google Drive file ID
        service: Optional pre-initialized Drive service
        credentials_path: Path to credentials JSON (if service not provided)
        
    Returns:
        Tuple of (file_bytes, file_metadata)
        
    Raises:
        HttpError: If file not found or permission denied
        Exception: For other errors
    """
    try:
        if service is None:
            service = get_drive_service(credentials_path)
        
        # Get file metadata
        file_metadata = service.files().get(
            fileId=file_id,
            fields='id,name,mimeType,size,createdTime,modifiedTime'
        ).execute()
        
        # Check if it's an image
        mime_type = file_metadata.get('mimeType', '')
        if not mime_type.startswith('image/'):
            raise ValueError(f"File is not an image. MIME type: {mime_type}")
        
        # Download file content
        request = service.files().get_media(fileId=file_id)
        file_stream = io.BytesIO()
        downloader = MediaIoBaseDownload(file_stream, request)
        
        done = False
        while not done:
            status, done = downloader.next_chunk()
        
        file_stream.seek(0)
        file_bytes = file_stream.read()
        
        return file_bytes, file_metadata
    
    except HttpError as e:
        if e.resp.status == 404:
            raise Exception("File not found. Make sure the file ID is correct and the file is shared.")
        elif e.resp.status == 403:
            raise Exception("Permission denied. Make sure the file is shared with the service account.")
        else:
            raise Exception(f"Google Drive API error: {str(e)}")
    except Exception as e:
        raise Exception(f"Failed to download file from Google Drive: {str(e)}")


def upload_from_google_drive_to_cloudinary(
    drive_file_id_or_url: str,
    cloudinary_folder: str = "uploads",
    public_id: Optional[str] = None,
    tags: Optional[list] = None,
    auto_compress: bool = True,
    max_size_bytes: int = TARGET_BYTES,
    credentials_path: Optional[str] = None
) -> Tuple[Dict[str, Any], str, str, Dict[str, Any]]:
    """
    Download an image from Google Drive, optionally compress it, and upload to Cloudinary.
    
    Args:
        drive_file_id_or_url: Google Drive file ID or shareable link
        cloudinary_folder: Cloudinary folder path (default: "uploads")
        public_id: Custom public ID for Cloudinary (default: uses Drive filename)
        tags: List of tags to add to the Cloudinary asset
        auto_compress: Whether to automatically compress large files
        max_size_bytes: Maximum size before compression (default: TARGET_BYTES from cloudinary_utils)
        credentials_path: Path to Google credentials JSON
        
    Returns:
        Tuple of (cloudinary_result, web_url, thumb_url, drive_metadata)
        
    Raises:
        Exception: If download or upload fails
    """
    try:
        # Extract file ID from URL if needed
        file_id = extract_file_id_from_url(drive_file_id_or_url)
        if not file_id:
            raise ValueError(f"Invalid Google Drive URL or file ID: {drive_file_id_or_url}")
        
        # Download file from Google Drive
        file_bytes, drive_metadata = download_file_from_drive(file_id, credentials_path=credentials_path)
        
        # Use Drive filename if public_id not provided
        if not public_id:
            from django.utils.text import slugify
            filename = drive_metadata.get('name', 'upload')
            # Remove extension
            base_name = filename.rsplit('.', 1)[0] if '.' in filename else filename
            public_id = slugify(base_name)[:120]
        
        # Auto-compress if file is too large
        if auto_compress and len(file_bytes) > max_size_bytes:
            print(f"File size ({len(file_bytes)} bytes) exceeds limit ({max_size_bytes} bytes). Compressing...")
            # Create a file-like object from bytes
            file_obj = io.BytesIO(file_bytes)
            file_bytes = smart_compress_to_bytes(file_obj)
            print(f"Compressed to {len(file_bytes)} bytes")
        
        # Upload to Cloudinary
        result, web_url, thumb_url = upload_to_cloudinary(
            file_bytes=file_bytes,
            folder=cloudinary_folder,
            public_id=public_id,
            tags=tags
        )
        
        return result, web_url, thumb_url, drive_metadata
    
    except Exception as e:
        raise Exception(f"Failed to upload from Google Drive to Cloudinary: {str(e)}")


def bulk_upload_from_drive_folder(
    folder_id: str,
    cloudinary_folder: str = "uploads",
    tags: Optional[list] = None,
    auto_compress: bool = True,
    credentials_path: Optional[str] = None,
    image_mime_types: Optional[list] = None
) -> list:
    """
    Upload all images from a Google Drive folder to Cloudinary.
    
    Args:
        folder_id: Google Drive folder ID
        cloudinary_folder: Cloudinary folder path
        tags: Tags to add to all uploaded images
        auto_compress: Whether to auto-compress large files
        credentials_path: Path to Google credentials JSON
        image_mime_types: List of allowed MIME types (default: common image formats)
        
    Returns:
        List of dicts with upload results and errors
    """
    if image_mime_types is None:
        image_mime_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp', 'image/bmp']
    
    results = []
    
    try:
        service = get_drive_service(credentials_path)
        
        # Query files in the folder
        query = f"'{folder_id}' in parents and trashed=false"
        response = service.files().list(
            q=query,
            fields='files(id,name,mimeType,size)',
            pageSize=100
        ).execute()
        
        files = response.get('files', [])
        
        for file in files:
            # Skip non-images
            if file.get('mimeType') not in image_mime_types:
                continue
            
            try:
                result, web_url, thumb_url, metadata = upload_from_google_drive_to_cloudinary(
                    drive_file_id_or_url=file['id'],
                    cloudinary_folder=cloudinary_folder,
                    tags=tags,
                    auto_compress=auto_compress,
                    credentials_path=credentials_path
                )
                
                results.append({
                    'success': True,
                    'drive_name': file['name'],
                    'drive_id': file['id'],
                    'cloudinary_url': web_url,
                    'public_id': result.get('public_id'),
                })
            except Exception as e:
                results.append({
                    'success': False,
                    'drive_name': file['name'],
                    'drive_id': file['id'],
                    'error': str(e)
                })
        
        return results
    
    except Exception as e:
        raise Exception(f"Failed to bulk upload from Drive folder: {str(e)}")


#!/usr/bin/env python
"""
Test script to check for MinIO-specific issues with head_object operations.

This script tests both standard S3Boto3Storage and the custom MinIOStorage
implementations against a MinIO server to determine if the 403 errors with
head_object operations occur in the current setup.

Usage:
    python test_minio_storage.py

Requirements:
    - Django
    - boto3
    - django-storages
    - An active MinIO server
"""

import os
import sys
import logging
import tempfile
import time
from io import BytesIO
from pathlib import Path

# Add the project root to the path so we can import from core
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('test_minio_storage')

# Import Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
import django
django.setup()

from django.conf import settings
from django.core.files.base import ContentFile
from storages.backends.s3boto3 import S3Boto3Storage
from botocore.exceptions import ClientError

# Try to import our custom MinIOStorage if it exists
try:
    from core.minio_storage import MinIOStorage
    HAS_MINIO_STORAGE = True
except ImportError:
    HAS_MINIO_STORAGE = False
    logger.warning("Custom MinIOStorage not found, will only test S3Boto3Storage")

# Test file types that might cause issues
TEST_FILE_TYPES = [
    ('text.txt', b'This is a text file', 'text/plain'),
    ('document.pdf', b'%PDF-1.5\n%Test PDF content', 'application/pdf'),
    ('image.jpg', b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff', 'image/jpeg'),
    ('image.png', b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82', 'image/png'),
]

def get_s3boto3_storage():
    """Create and return a standard S3Boto3Storage instance."""
    # Check if we have MinIO configuration
    if not hasattr(settings, 'AWS_S3_ENDPOINT_URL') or not settings.AWS_S3_ENDPOINT_URL:
        logger.error("MinIO endpoint URL not configured in settings")
        sys.exit(1)
        
    logger.info(f"Creating S3Boto3Storage with endpoint: {settings.AWS_S3_ENDPOINT_URL}")
    
    # Create storage instance with MinIO configuration
    return S3Boto3Storage(
        access_key=getattr(settings, 'AWS_ACCESS_KEY_ID', None),
        secret_key=getattr(settings, 'AWS_SECRET_ACCESS_KEY', None),
        bucket_name=getattr(settings, 'AWS_STORAGE_BUCKET_NAME', None),
        endpoint_url=settings.AWS_S3_ENDPOINT_URL,
        region_name=getattr(settings, 'AWS_S3_REGION_NAME', None),
        custom_domain=None,
        use_ssl=getattr(settings, 'AWS_S3_USE_SSL', True),
        verify=getattr(settings, 'AWS_S3_VERIFY', None),
    )

def get_minio_storage():
    """Create and return a MinIOStorage instance if available."""
    if not HAS_MINIO_STORAGE:
        return None
        
    logger.info(f"Creating MinIOStorage with endpoint: {settings.AWS_S3_ENDPOINT_URL}")
    
    # Create storage instance with MinIO configuration
    return MinIOStorage(
        access_key=getattr(settings, 'AWS_ACCESS_KEY_ID', None),
        secret_key=getattr(settings, 'AWS_SECRET_ACCESS_KEY', None),
        bucket_name=getattr(settings, 'AWS_STORAGE_BUCKET_NAME', None),
        endpoint_url=settings.AWS_S3_ENDPOINT_URL,
        region_name=getattr(settings, 'AWS_S3_REGION_NAME', None),
        custom_domain=None,
        use_ssl=getattr(settings, 'AWS_S3_USE_SSL', True),
        verify=getattr(settings, 'AWS_S3_VERIFY', None),
    )

def test_storage_operations(storage, storage_name):
    """Test basic storage operations."""
    logger.info(f"Testing {storage_name} operations...")
    
    # Test directory for this run
    test_dir = f"test_storage_{int(time.time())}"
    
    results = {
        'save': {'success': 0, 'failure': 0, 'errors': []},
        'exists': {'success': 0, 'failure': 0, 'errors': []},
        'open': {'success': 0, 'failure': 0, 'errors': []},
        'size': {'success': 0, 'failure': 0, 'errors': []},
        'delete': {'success': 0, 'failure': 0, 'errors': []},
        'head_object': {'success': 0, 'failure': 0, 'errors': []},
    }
    
    saved_files = []
    
    # Test each file type
    for filename, content, content_type in TEST_FILE_TYPES:
        file_path = f"{test_dir}/{filename}"
        logger.info(f"Testing with file: {file_path}")
        
        # Test save operation
        try:
            file_obj = ContentFile(content, name=filename)
            saved_path = storage.save(file_path, file_obj)
            logger.info(f"Successfully saved file: {saved_path}")
            saved_files.append(saved_path)
            results['save']['success'] += 1
        except Exception as e:
            logger.error(f"Error saving file {file_path}: {str(e)}")
            results['save']['failure'] += 1
            results['save']['errors'].append(str(e))
            continue
        
        # Test exists operation
        try:
            exists = storage.exists(saved_path)
            logger.info(f"File exists check: {exists}")
            if exists:
                results['exists']['success'] += 1
            else:
                results['exists']['failure'] += 1
                results['exists']['errors'].append(f"File should exist but doesn't: {saved_path}")
        except Exception as e:
            logger.error(f"Error checking if file exists {saved_path}: {str(e)}")
            results['exists']['failure'] += 1
            results['exists']['errors'].append(str(e))
        
        # Test open operation
        try:
            file_obj = storage.open(saved_path)
            file_content = file_obj.read()
            logger.info(f"Successfully opened file: {saved_path}, content length: {len(file_content)}")
            results['open']['success'] += 1
        except Exception as e:
            logger.error(f"Error opening file {saved_path}: {str(e)}")
            results['open']['failure'] += 1
            results['open']['errors'].append(str(e))
        
        # Test size operation
        try:
            size = storage.size(saved_path)
            logger.info(f"File size: {size}")
            results['size']['success'] += 1
        except Exception as e:
            logger.error(f"Error getting file size {saved_path}: {str(e)}")
            results['size']['failure'] += 1
            results['size']['errors'].append(str(e))
        
        # Test direct head_object operation (this is what might cause 403 errors)
        try:
            if hasattr(storage, 'connection'):
                metadata = storage.connection.meta.client.head_object(
                    Bucket=storage.bucket_name,
                    Key=saved_path
                )
                logger.info(f"Successfully performed head_object: {metadata}")
                results['head_object']['success'] += 1
            else:
                logger.warning("Storage doesn't have connection attribute, skipping head_object test")
        except Exception as e:
            logger.error(f"Error performing head_object on {saved_path}: {str(e)}")
            results['head_object']['failure'] += 1
            results['head_object']['errors'].append(str(e))
    
    # Clean up test files
    for file_path in saved_files:
        try:
            storage.delete(file_path)
            logger.info(f"Successfully deleted file: {file_path}")
            results['delete']['success'] += 1
        except Exception as e:
            logger.error(f"Error deleting file {file_path}: {str(e)}")
            results['delete']['failure'] += 1
            results['delete']['errors'].append(str(e))
    
    return results

def print_results(results, storage_name):
    """Print test results in a readable format."""
    print(f"\n{'=' * 50}")
    print(f"Results for {storage_name}")
    print(f"{'=' * 50}")
    
    for operation, stats in results.items():
        success_rate = 0
        if stats['success'] + stats['failure'] > 0:
            success_rate = (stats['success'] / (stats['success'] + stats['failure'])) * 100
            
        print(f"{operation.upper()}: {stats['success']} succeeded, {stats['failure']} failed ({success_rate:.1f}% success)")
        
        if stats['errors']:
            print("  Errors:")
            for i, error in enumerate(stats['errors'], 1):
                print(f"  {i}. {error}")
    
    print(f"{'=' * 50}\n")

def main():
    """Main test function."""
    print("\nTesting MinIO Storage Operations")
    print("===============================\n")
    
    # Test with standard S3Boto3Storage
    try:
        s3_storage = get_s3boto3_storage()
        s3_results = test_storage_operations(s3_storage, "S3Boto3Storage")
        print_results(s3_results, "S3Boto3Storage")
    except Exception as e:
        logger.error(f"Error testing S3Boto3Storage: {str(e)}")
    
    # Test with custom MinIOStorage if available
    if HAS_MINIO_STORAGE:
        try:
            minio_storage = get_minio_storage()
            minio_results = test_storage_operations(minio_storage, "MinIOStorage")
            print_results(minio_results, "MinIOStorage")
        except Exception as e:
            logger.error(f"Error testing MinIOStorage: {str(e)}")
    
    print("\nTest completed. Check the results above to determine if you need the custom MinIOStorage class.")
    print("If S3Boto3Storage has failures with head_object operations but MinIOStorage succeeds, you should use MinIOStorage.")
    print("If both succeed or both fail, you can use the standard S3Boto3Storage.")

if __name__ == "__main__":
    main()

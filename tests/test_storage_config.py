#!/usr/bin/env python
"""
Test script to check if the storage configuration is working correctly.

This script tests the storage configuration by:
1. Creating a test file using default_storage
2. Checking if the file exists
3. Reading the file content
4. Getting the file URL
5. Deleting the file

Usage:
    python test_storage_config.py
"""

import os
import sys
import logging
from pathlib import Path

# Add the project root to the path so we can import from core
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('test_storage_config')

# Import Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
import django
django.setup()

from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from core.storage import SecureFileStorage

def test_default_storage():
    """Test the default_storage configuration."""
    logger.info("Testing default_storage configuration...")
    
    # Create a test file
    test_file_path = f"test_storage_{os.urandom(4).hex()}.txt"
    test_content = f"Test content: {os.urandom(8).hex()}"
    
    logger.info(f"Creating test file: {test_file_path}")
    path = default_storage.save(test_file_path, ContentFile(test_content.encode()))
    
    # Check if the file exists
    logger.info(f"Checking if file exists: {path}")
    exists = default_storage.exists(path)
    logger.info(f"File exists: {exists}")
    
    # Read the file content
    if exists:
        logger.info(f"Reading file content: {path}")
        content = default_storage.open(path).read().decode()
        logger.info(f"File content: {content}")
        
        # Check if the content matches
        if content == test_content:
            logger.info("File content matches the original content")
        else:
            logger.error("File content does not match the original content")
    
    # Get the file URL
    logger.info(f"Getting file URL: {path}")
    url = default_storage.url(path)
    logger.info(f"File URL: {url}")
    
    # Delete the file
    logger.info(f"Deleting file: {path}")
    default_storage.delete(path)
    
    # Check if the file was deleted
    logger.info(f"Checking if file was deleted: {path}")
    exists = default_storage.exists(path)
    logger.info(f"File exists after deletion: {exists}")
    
    return not exists

def test_secure_file_storage():
    """Test the SecureFileStorage configuration."""
    logger.info("Testing SecureFileStorage configuration...")
    
    # Create a SecureFileStorage instance
    secure_storage = SecureFileStorage(private=True, collection='test_collection')
    
    # Create a test file
    test_file_path = f"test_secure_storage_{os.urandom(4).hex()}.txt"
    test_content = f"Test content: {os.urandom(8).hex()}"
    
    logger.info(f"Creating test file: {test_file_path}")
    path = secure_storage.save(test_file_path, ContentFile(test_content.encode()))
    
    # Check if the file exists
    logger.info(f"Checking if file exists: {path}")
    exists = secure_storage.exists(path)
    logger.info(f"File exists: {exists}")
    
    # Read the file content
    if exists:
        logger.info(f"Reading file content: {path}")
        content = secure_storage.open(path).read().decode()
        logger.info(f"File content: {content}")
        
        # Check if the content matches
        if content == test_content:
            logger.info("File content matches the original content")
        else:
            logger.error("File content does not match the original content")
    
    # Get the file URL
    logger.info(f"Getting file URL: {path}")
    url = secure_storage.url(path)
    logger.info(f"File URL: {url}")
    
    # Delete the file
    logger.info(f"Deleting file: {path}")
    secure_storage.delete(path)
    
    # Check if the file was deleted
    logger.info(f"Checking if file was deleted: {path}")
    exists = secure_storage.exists(path)
    logger.info(f"File exists after deletion: {exists}")
    
    return not exists

def main():
    """Main test function."""
    print("\nTesting Storage Configuration")
    print("===========================\n")
    
    # Test default_storage
    try:
        default_storage_success = test_default_storage()
        print(f"\ndefault_storage test {'succeeded' if default_storage_success else 'failed'}")
    except Exception as e:
        logger.error(f"Error testing default_storage: {str(e)}")
        print(f"\ndefault_storage test failed with error: {str(e)}")
    
    # Test SecureFileStorage
    try:
        secure_storage_success = test_secure_file_storage()
        print(f"\nSecureFileStorage test {'succeeded' if secure_storage_success else 'failed'}")
    except Exception as e:
        logger.error(f"Error testing SecureFileStorage: {str(e)}")
        print(f"\nSecureFileStorage test failed with error: {str(e)}")
    
    print("\nTest completed.")

if __name__ == "__main__":
    main()

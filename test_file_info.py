#!/usr/bin/env python
"""
Automated test script for file information functionality.
This script will:
1. Create a test file
2. Set file information (description and favorite status)
3. Verify the information is saved in the database
4. Verify the information can be retrieved via the API
5. Update the information and verify the changes
"""

import os
import sys
import json
import requests
import django
import time
from urllib.parse import quote

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

# Import Django models
from apps.file_manager.models import FileInfo
from django.contrib.auth import get_user_model
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

User = get_user_model()

# Configuration
SERVER_URL = 'http://localhost:9001'
TEST_USER_EMAIL = 'vikas@neuralami.ai'  # User's email
TEST_USER_PASSWORD = 'kaajal1'  # User's password
TEST_FILE_CONTENT = b'Test file content'
TEST_FILE_NAME = f'test_file_{int(time.time())}.txt'
TEST_DESCRIPTION = f'Test description {int(time.time())}'
TEST_FAVORITE = True

def get_user():
    """Get the first superuser"""
    superusers = User.objects.filter(is_superuser=True)
    if superusers.exists():
        user = superusers.first()
        print(f"Using superuser: {user.email}")
        return user
    else:
        print("❌ No superuser found. Please create a superuser first.")
        sys.exit(1)

def create_test_file(user):
    """Create a test file in the user's directory"""
    user_id = str(user.id)
    file_path = f"{user_id}/{TEST_FILE_NAME}"

    # Delete the file if it exists
    if default_storage.exists(file_path):
        default_storage.delete(file_path)

    # Create the file
    path = default_storage.save(file_path, ContentFile(TEST_FILE_CONTENT))
    print(f"✅ Created test file: {path}")
    return path

def set_file_info(user, file_path):
    """Set file information directly in the database"""
    # Delete existing file info if it exists
    FileInfo.objects.filter(path=file_path).delete()

    # Create new file info
    file_info = FileInfo.objects.create(
        user=user,
        path=file_path,
        filename=os.path.basename(file_path),
        info=TEST_DESCRIPTION,
        is_favorite=TEST_FAVORITE
    )
    print(f"✅ Set file info: {file_info.info}, favorite: {file_info.is_favorite}")
    return file_info

def verify_database_info(file_path):
    """Verify the file information is saved in the database"""
    try:
        file_info = FileInfo.objects.get(path=file_path)
        print(f"Database info: {file_info.info}, favorite: {file_info.is_favorite}")

        if file_info.info == TEST_DESCRIPTION and file_info.is_favorite == TEST_FAVORITE:
            print("✅ Database verification passed")
            return True
        else:
            print("❌ Database verification failed")
            return False
    except FileInfo.DoesNotExist:
        print("❌ File info not found in database")
        return False

def get_session():
    """Get a session with login"""
    session = requests.Session()

    # Get the login page to get the CSRF token
    login_url = f"{SERVER_URL}/accounts/login/"
    response = session.get(login_url)

    # Extract CSRF token
    csrf_token = None
    for line in response.text.split('\n'):
        if 'csrfmiddlewaretoken' in line:
            start = line.find('value="') + 7
            end = line.find('"', start)
            csrf_token = line[start:end]
            break

    if not csrf_token:
        print("❌ Could not extract CSRF token")
        return None

    # Login
    login_data = {
        'csrfmiddlewaretoken': csrf_token,
        'email': TEST_USER_EMAIL,
        'password': TEST_USER_PASSWORD
    }

    response = session.post(login_url, data=login_data, headers={'Referer': login_url})

    if response.status_code == 200 and 'dashboard' in response.url:
        print("✅ Login successful")
        return session
    else:
        print(f"❌ Login failed: {response.status_code}")
        return None

def get_file_info_via_api(session, file_path):
    """Get file information via the API"""
    encoded_path = quote(file_path)
    url = f"{SERVER_URL}/file-manager/get-file-info/?file_path={encoded_path}"

    try:
        response = session.get(url)

        if response.status_code != 200:
            print(f"❌ API request failed: {response.status_code}")
            return None

        data = response.json()
        print(f"API response: {data}")
        return data
    except Exception as e:
        print(f"❌ Error getting file info via API: {e}")
        return None

def verify_api_info(data):
    """Verify the file information from the API"""
    if not data:
        return False

    if data.get('success') and data.get('info') == TEST_DESCRIPTION and data.get('is_favorite') == TEST_FAVORITE:
        print("✅ API verification passed")
        return True
    else:
        print("❌ API verification failed")
        return False

def update_file_info_via_api(session, file_path):
    """Update file information via the API"""
    encoded_path = quote(file_path)
    url = f"{SERVER_URL}/file-manager/save-info/{encoded_path}/"

    # Generate new test values
    new_description = f"Updated description {int(time.time())}"
    new_favorite = not TEST_FAVORITE

    try:
        # Get CSRF token from the file manager page
        response = session.get(f"{SERVER_URL}/file-manager/")

        # Extract CSRF token
        csrf_token = None
        for line in response.text.split('\n'):
            if 'csrfmiddlewaretoken' in line:
                start = line.find('value="') + 7
                end = line.find('"', start)
                csrf_token = line[start:end]
                break

        if not csrf_token:
            print("❌ Could not extract CSRF token")
            return None

        # Prepare data
        data = {
            'csrfmiddlewaretoken': csrf_token,
            'info': new_description
        }

        # Add is_favorite if true
        if new_favorite:
            data['is_favorite'] = 'on'

        # Send the request
        headers = {
            'Referer': f"{SERVER_URL}/file-manager/",
            'X-CSRFToken': csrf_token,
            'HX-Request': 'true'
        }

        response = session.post(url, data=data, headers=headers)

        if response.status_code != 200:
            print(f"❌ Update request failed: {response.status_code}")
            return None

        print(f"✅ Updated file info via API: {new_description}, favorite: {new_favorite}")
        return {
            'description': new_description,
            'favorite': new_favorite
        }
    except Exception as e:
        print(f"❌ Error updating file info via API: {e}")
        return None

def verify_updated_info(file_path, updated_info):
    """Verify the updated file information"""
    if not updated_info:
        return False

    try:
        # Verify in database
        file_info = FileInfo.objects.get(path=file_path)
        db_verified = (file_info.info == updated_info['description'] and
                      file_info.is_favorite == updated_info['favorite'])

        if db_verified:
            print("✅ Updated info verification passed in database")
            return True
        else:
            print("❌ Updated info verification failed in database")
            print(f"Expected: {updated_info['description']}, {updated_info['favorite']}")
            print(f"Actual: {file_info.info}, {file_info.is_favorite}")
            return False
    except Exception as e:
        print(f"❌ Error verifying updated info: {e}")
        return False

def main():
    """Main test function"""
    print("\n=== Starting File Information Persistence Test ===\n")

    # Get user
    user = get_user()

    # Create test file
    file_path = create_test_file(user)

    # Set file info
    set_file_info(user, file_path)

    # Verify database info
    db_verified = verify_database_info(file_path)

    # Update file info directly in the database
    new_description = f"Updated description {int(time.time())}"
    new_favorite = not TEST_FAVORITE

    # Get the file info
    file_info = FileInfo.objects.get(path=file_path)

    # Update the file info
    file_info.info = new_description
    file_info.is_favorite = new_favorite
    file_info.save()

    print(f"✅ Updated file info directly: {new_description}, favorite: {new_favorite}")

    # Verify the update
    file_info.refresh_from_db()
    update_verified = (file_info.info == new_description and file_info.is_favorite == new_favorite)

    if update_verified:
        print("✅ Update verification passed")
    else:
        print("❌ Update verification failed")
        print(f"Expected: {new_description}, {new_favorite}")
        print(f"Actual: {file_info.info}, {file_info.is_favorite}")

    # Print final results
    print("\n=== Test Results ===")
    print(f"Database verification: {'✅ PASSED' if db_verified else '❌ FAILED'}")
    print(f"Update verification: {'✅ PASSED' if update_verified else '❌ FAILED'}")

    if db_verified and update_verified:
        print("\n✅ All tests passed! File information is persisting correctly in the database.")
        return 0
    else:
        print("\n❌ Some tests failed. File information is not persisting correctly.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

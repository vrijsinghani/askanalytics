"""
Test script to verify core settings configuration.

This script tests various aspects of the Django settings configuration:
- Environment variables
- Database connection
- SecureFileStorage
- Redis cache
- Celery configuration
- WebSocket configuration
- Logging configuration

Run with: python manage.py shell < tests/scripts/test_settings.py
"""

import os
import sys
import json
import django
from django.conf import settings
from django.core.cache import cache
from django.core.files.base import ContentFile
from django.utils import timezone

# Set up colorful output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 80}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(80)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'=' * 80}{Colors.ENDC}\n")

def print_success(text):
    print(f"{Colors.OKGREEN}✓ {text}{Colors.ENDC}")

def print_warning(text):
    print(f"{Colors.WARNING}⚠ {text}{Colors.ENDC}")

def print_error(text):
    print(f"{Colors.FAIL}✗ {text}{Colors.ENDC}")

def print_info(text):
    print(f"{Colors.OKBLUE}ℹ {text}{Colors.ENDC}")

# Test environment variables
def test_env_vars():
    print_header("Testing Environment Variables")
    
    required_vars = [
        'SECRET_KEY', 
        'DEBUG', 
        'DB_ENGINE', 
        'DB_NAME', 
        'DB_USERNAME',
        'APP_DOMAIN',
    ]
    
    for var in required_vars:
        value = os.environ.get(var)
        if value:
            print_success(f"{var} is set to: {value if var != 'SECRET_KEY' else '********'}")
        else:
            print_error(f"{var} is not set!")
    
    # Check if DEBUG is properly parsed as boolean
    debug_value = settings.DEBUG
    print_info(f"DEBUG setting parsed as: {debug_value} (type: {type(debug_value).__name__})")
    
    # Check CSRF_TRUSTED_ORIGINS
    print_info(f"CSRF_TRUSTED_ORIGINS: {settings.CSRF_TRUSTED_ORIGINS}")

# Test database connection
def test_database():
    print_header("Testing Database Connection")
    
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT version();")
            version = cursor.fetchone()[0]
            print_success(f"Connected to database: {version}")
            
            # Test connection pooling
            print_info(f"Connection max age: {settings.DATABASES['default'].get('CONN_MAX_AGE', 'Not set')}")
            
    except Exception as e:
        print_error(f"Database connection failed: {str(e)}")

# Test SecureFileStorage
def test_secure_storage():
    print_header("Testing SecureFileStorage")
    
    try:
        from core.storage import SecureFileStorage
        
        # Create a test storage instance
        storage = SecureFileStorage(private=True, collection='test')
        
        # Test basic properties
        print_info(f"Storage is private: {storage.private}")
        print_info(f"Storage collection: {storage.collection}")
        
        # Test path generation
        test_path = storage._get_path("test_file.txt")
        print_info(f"Generated path: {test_path}")
        
        # Test URL generation
        test_url = storage.url("test_file.txt")
        print_info(f"Generated URL: {test_url}")
        
        print_success("SecureFileStorage is properly configured")
        
    except Exception as e:
        print_error(f"SecureFileStorage test failed: {str(e)}")

# Test Redis and cache
def test_redis_cache():
    print_header("Testing Redis Cache")
    
    try:
        # Test cache connection
        test_key = f"test_key_{timezone.now().timestamp()}"
        test_value = {"timestamp": str(timezone.now()), "test": True}
        
        # Set value in cache
        cache.set(test_key, test_value, timeout=60)
        
        # Get value from cache
        retrieved_value = cache.get(test_key)
        
        if retrieved_value == test_value:
            print_success(f"Cache test passed: {test_key} = {retrieved_value}")
        else:
            print_error(f"Cache test failed: Expected {test_value}, got {retrieved_value}")
            
        # Delete test key
        cache.delete(test_key)
        
        # Check cache backend
        print_info(f"Cache backend: {settings.CACHES['default']['BACKEND']}")
        print_info(f"Cache location: {settings.CACHES['default']['LOCATION']}")
        
    except Exception as e:
        print_error(f"Redis cache test failed: {str(e)}")

# Test Celery configuration
def test_celery_config():
    print_header("Testing Celery Configuration")
    
    try:
        # Check Celery settings
        print_info(f"Broker URL: {settings.CELERY_BROKER_URL}")
        print_info(f"Result Backend: {settings.CELERY_RESULT_BACKEND}")
        print_info(f"Task Serializer: {settings.CELERY_TASK_SERIALIZER}")
        print_info(f"Result Serializer: {settings.CELERY_RESULT_SERIALIZER}")
        print_info(f"Task Time Limit: {settings.CELERY_TASK_TIME_LIMIT}")
        
        # Check if django_celery_results is installed
        if 'django_celery_results' in settings.INSTALLED_APPS:
            print_success("django_celery_results is installed")
        else:
            print_warning("django_celery_results is not installed")
            
        # Check if django_celery_beat is installed
        if 'django_celery_beat' in settings.INSTALLED_APPS:
            print_success("django_celery_beat is installed")
        else:
            print_warning("django_celery_beat is not installed")
            
    except Exception as e:
        print_error(f"Celery configuration test failed: {str(e)}")

# Test WebSocket configuration
def test_websocket_config():
    print_header("Testing WebSocket Configuration")
    
    try:
        # Check Channels settings
        print_info(f"ASGI Application: {settings.ASGI_APPLICATION}")
        
        # Check channel layers
        if hasattr(settings, 'CHANNEL_LAYERS'):
            backend = settings.CHANNEL_LAYERS['default']['BACKEND']
            config = settings.CHANNEL_LAYERS['default']['CONFIG']
            print_success(f"Channel Layers configured with backend: {backend}")
            print_info(f"Channel Layers config: {config}")
        else:
            print_error("CHANNEL_LAYERS not configured")
            
        # Check if channels is installed
        if 'channels' in settings.INSTALLED_APPS:
            print_success("channels is installed")
        else:
            print_warning("channels is not installed")
            
        # Import the websocket consumer to verify it exists
        try:
            from apps.websockets.consumers.notification import NotificationConsumer
            print_success("NotificationConsumer is available")
        except ImportError as e:
            print_error(f"Could not import NotificationConsumer: {str(e)}")
            
    except Exception as e:
        print_error(f"WebSocket configuration test failed: {str(e)}")

# Test logging configuration
def test_logging_config():
    print_header("Testing Logging Configuration")
    
    try:
        import logging
        
        # Check logging configuration
        print_info(f"Logging version: {settings.LOGGING['version']}")
        print_info(f"Disable existing loggers: {settings.LOGGING['disable_existing_loggers']}")
        
        # Check formatters
        formatters = list(settings.LOGGING['formatters'].keys())
        print_info(f"Configured formatters: {formatters}")
        
        # Check handlers
        handlers = list(settings.LOGGING['handlers'].keys())
        print_info(f"Configured handlers: {handlers}")
        
        # Check loggers
        loggers = list(settings.LOGGING['loggers'].keys())
        print_info(f"Configured loggers: {loggers}")
        
        # Test logging
        logger = logging.getLogger('core')
        logger.info("Test log message from settings test script")
        print_success("Logged test message to 'core' logger")
        
    except Exception as e:
        print_error(f"Logging configuration test failed: {str(e)}")

# Run all tests
def run_all_tests():
    print_header("SETTINGS CONFIGURATION TEST")
    print(f"Django version: {django.get_version()}")
    print(f"Python version: {sys.version}")
    print(f"Testing at: {timezone.now()}")
    
    test_env_vars()
    test_database()
    test_secure_storage()
    test_redis_cache()
    test_celery_config()
    test_websocket_config()
    test_logging_config()
    
    print_header("TEST COMPLETE")

# Run the tests
run_all_tests()

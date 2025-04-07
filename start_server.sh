#!/bin/bash
PROJECT_DIR="$(dirname "$0")"  # Get project root directory
cd "$PROJECT_DIR"  # Change to project root directory
echo "Current directory: $(pwd)"

# Add the project directory to PYTHONPATH
export PYTHONPATH="$PROJECT_DIR:$PYTHONPATH"
export DJANGO_SETTINGS_MODULE="core.settings"

# Create directories for logs and pids if they don't exist
mkdir -p logs pids

# Ensure we're using the virtual environment
source .venv/bin/activate

# Start Uvicorn with nohup - using correct lifespan option
echo "Starting Uvicorn ASGI server..."
PYTHONPATH="$PROJECT_DIR" nohup python -m uvicorn core.asgi:application --host 0.0.0.0 --port 8999 --lifespan off --ws websockets --ws-ping-interval 50 --ws-ping-timeout 60 > ./logs/django_stdout.log 2>&1 &
echo $! > ./pids/django.pid

# Start Celery worker with nohup
echo "Starting Celery worker..."
PYTHONPATH="$PROJECT_DIR" nohup python -m celery -A apps.tasks worker -l info > ./logs/celery.log 2>&1 &
echo $! > ./pids/celery.pid

# Start Celery beat with nohup
echo "Starting Celery beat..."
PYTHONPATH="$PROJECT_DIR" nohup python -m celery -A apps.tasks beat -l info > ./logs/celerybeat.log 2>&1 &
echo $! > ./pids/celerybeat.pid

echo "Services started successfully"
echo "Uvicorn server running at http://0.0.0.0:8999/"

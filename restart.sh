#!/bin/bash

# Get the directory where the script is located
PROJECT_DIR="$(dirname "$0")"
cd "$PROJECT_DIR"

echo "Restarting services..."

# Stop all services
echo "Stopping services..."
./stopservices.sh

echo "Waiting for services to stop completely..."
sleep 3

# Clear Celery tasks and ensure all processes are stopped
echo "Checking for remaining processes..."

# Handle lingering Celery processes
if pgrep -f 'celery -A apps.tasks' >/dev/null 2>&1; then
    echo "Attempting to stop remaining Celery processes..."
    pkill -SIGTERM -f 'celery -A apps.tasks' 2>/dev/null
    sleep 2
    pkill -SIGKILL -f 'celery -A apps.tasks' 2>/dev/null
fi

# Handle ASGI server processes (Uvicorn)
echo "Ensuring ASGI server is stopped..."
if pgrep -f 'uvicorn.*core.asgi' >/dev/null 2>&1; then
    echo "Stopping Uvicorn processes..."
    pkill -SIGTERM -f 'uvicorn.*core.asgi' 2>/dev/null
    sleep 2
    # If processes still exist, try force kill
    if pgrep -f 'uvicorn.*core.asgi' >/dev/null 2>&1; then
        echo "Force stopping remaining Uvicorn processes..."
        pkill -SIGKILL -f 'uvicorn.*core.asgi' 2>/dev/null
    fi
fi

# Activate virtual environment
source .venv/bin/activate

# Clear the Celery queue
echo "Clearing Celery queue..."
celery -A apps.tasks purge -f >/dev/null 2>&1

# Clear log files
echo "Clearing log files..."
mkdir -p ./logs
echo -n > ./logs/django.log
echo -n > ./logs/django_stdout.log
echo -n > ./logs/celery.log
echo -n > ./logs/celerybeat.log

# Start services
echo "Starting services..."
./start_server.sh

echo "Services have been restarted successfully"

#!/bin/bash

# Get the number of workers based on CPU cores
WORKERS=${WORKERS:-$(( 2 * $(nproc --all) ))}
# Ensure at least 2 workers
if [ "$WORKERS" -lt "2" ]; then
    WORKERS=2
fi

echo "Starting Uvicorn with $WORKERS workers"

# Start Uvicorn with the specified settings - using correct lifespan option
exec uvicorn core.asgi:application \
    --host 0.0.0.0 \
    --port ${APP_PORT:-8000} \
    --workers $WORKERS \
    --lifespan off \
    --ws websockets \
    --ws-ping-interval 50 \
    --ws-ping-timeout 60

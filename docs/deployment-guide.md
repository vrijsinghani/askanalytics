# Deployment Guide

This document outlines the production deployment process for the AskAnalytics project.

## 1. Docker-based Deployment Architecture

### 1.1. Container Components
- **Main Application Container**: Django application running with Uvicorn (ASGI server)
- **Celery Worker Container**: For background task processing
- **Celery Beat Container**: For scheduled tasks
- **Redis Container**: For caching, session storage, and Celery broker

### 1.2. Docker Image Building
- Use multi-stage builds for optimized images
- Separate images for application and worker containers
- Include version and commit information in image metadata
- Implement proper health checks for all containers

### 1.3. Environment Configuration
- Use environment variables for configuration
- Store sensitive information in environment files
- Implement different configurations for development and production

## 2. Deployment Workflow

### 2.1. Build Process
```bash
# Update requirements
uv pip freeze > requirements.txt

# Build Docker images
./build-docker-images.sh
```

### 2.2. Deployment Process
```bash
# Pull latest images
docker-compose pull

# Update services
docker-compose up -d

# Verify deployment
docker-compose ps
```

### 2.3. Database Migration Handling
- Run migrations during deployment with `RUN_MIGRATIONS=true`
- Use entrypoint script to wait for database availability
- Implement proper error handling for migration failures

## 3. Required Deployment Scripts

### 3.1. build-docker-images.sh
- Script to build and tag Docker images
- Includes version information from git
- Pushes images to registry

Example:
```bash
#!/bin/bash
set -e  # Exit immediately if a command exits with a non-zero status

# Configuration
REGISTRY="your-registry-url"
PROJECT="askanalytics"
VERSION=$(git describe --tags --always --dirty || echo "latest")
COMMIT=$(git rev-parse --short HEAD || echo "unknown")
COMMIT_DATE=$(git show -s --format=%ct HEAD || echo $(date +%s))

echo "Building Docker images for $PROJECT version: $VERSION (commit: $COMMIT, date: $COMMIT_DATE)"

# Ensure requirements.txt is up to date
echo "Updating requirements.txt..."
cp requirements.txt requirements.frozen.txt

# Clean and collect static files
echo "Cleaning and collecting static files..."
source .venv/bin/activate
python manage.py collectstatic --clear --noinput
deactivate

# Build the main application image
echo "Building main application image..."
docker build \
    --build-arg BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ') \
    --build-arg VERSION="$VERSION" \
    --build-arg COMMIT="$COMMIT" \
    --build-arg COMMIT_DATE="$COMMIT_DATE" \
    -t "$REGISTRY/$PROJECT:$VERSION" \
    -t "$REGISTRY/$PROJECT:latest" \
    .

# Build the worker image (used for both celery_worker and celery_beat)
echo "Building worker image..."
docker build \
    --build-arg BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ') \
    --build-arg VERSION="$VERSION" \
    --build-arg COMMIT="$COMMIT" \
    --build-arg COMMIT_DATE="$COMMIT_DATE" \
    -t "$REGISTRY/$PROJECT-worker:$VERSION" \
    -t "$REGISTRY/$PROJECT-worker:latest" \
    -f worker/Dockerfile \
    .

# Push images to registry
echo "Pushing images to registry..."
docker push "$REGISTRY/$PROJECT:$VERSION"
docker push "$REGISTRY/$PROJECT:latest"
docker push "$REGISTRY/$PROJECT-worker:$VERSION"
docker push "$REGISTRY/$PROJECT-worker:latest"
docker system prune -f
echo "Docker build and push completed successfully!"
```

### 3.2. entrypoint.sh
- Container entrypoint script
- Handles database connection verification
- Runs migrations when configured
- Sets up proper environment

Example:
```bash
#!/bin/bash
set -e

# Wait for database to be ready (optional but recommended)
if [ "$WAIT_FOR_DB" = "true" ]; then
    echo "Waiting for database to be ready..."
    python -c "
import sys
import time
import psycopg2
from os import environ

host = environ.get('DB_HOST', 'localhost')
port = environ.get('DB_PORT', '5432')
dbname = environ.get('DB_NAME', 'postgres')
user = environ.get('DB_USERNAME', 'postgres')
password = environ.get('DB_PASS', '')

for i in range(30):
    try:
        conn = psycopg2.connect(f'dbname={dbname} user={user} password={password} host={host} port={port}')
        conn.close()
        print('Database is ready!')
        break
    except psycopg2.OperationalError:
        print('Database not ready yet. Waiting...')
        time.sleep(2)
else:
    print('Could not connect to database after 30 attempts. Exiting.')
    sys.exit(1)
"
fi

# Run migrations if requested
if [ "$RUN_MIGRATIONS" = "true" ]; then
    echo "Running database migrations..."
    
    # Only run makemigrations in development environments
    if [ "$DJANGO_ENV" = "development" ]; then
        echo "Creating migrations (development only)..."
        python manage.py makemigrations
    fi
    
    echo "Applying migrations..."
    python manage.py migrate
    
    # Optionally collect static files
    if [ "$COLLECT_STATIC" = "true" ]; then
        echo "Collecting static files..."
        python manage.py collectstatic --noinput
    fi
fi

# Execute the main command
echo "Starting application..."
exec "$@"
```

### 3.3. start_server.sh
- Starts the ASGI server (Uvicorn)
- Configures WebSocket support
- Sets proper worker parameters

Example:
```bash
#!/bin/bash

# Start Uvicorn with the specified settings - using correct lifespan option
exec uvicorn core.asgi:application --host 0.0.0.0 --port ${APP_PORT:-3010} --lifespan off --ws websockets --ws-ping-interval 50 --ws-ping-timeout 60
```

### 3.4. update-services.sh
- Pulls latest images
- Updates running containers
- Performs cleanup of old images

Example:
```bash
#!/bin/bash
set -e

echo "Pulling latest images..."
docker-compose pull

echo "Updating services..."
docker-compose up -d

echo "Verifying update..."
docker-compose ps

echo "Cleaning up old images..."
docker image prune -f

echo "Update completed successfully!"
```

### 3.5. docker-compose.yml
- Defines all services (app, worker, beat, redis)
- Configures networking between services
- Sets up volumes and environment variables
- Implements health checks

Example:
```yaml
version: "3.9"
services:
  askanalytics:
    image: your-registry-url/askanalytics:latest
    networks:
      - db_network
      - web_network
    env_file: ".env"
    environment:
      - RUN_MIGRATIONS=${RUN_MIGRATIONS:-false}
      - WAIT_FOR_DB=true
      - COLLECT_STATIC=${COLLECT_STATIC:-false}
    depends_on:
      redis:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:${APP_PORT:-3010}/health/"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    restart: unless-stopped
    ports:
      - "${APP_PORT:-3010}:${APP_PORT:-3010}"

  redis:
    image: redis:latest
    command: redis-server
    volumes:
      - redis_data:/data
    ports:
      - "6380:6379"
    networks:
      - db_network
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: always

  askanalytics-worker:
    image: your-registry-url/askanalytics-worker:latest
    env_file: ".env"
    networks:
      - db_network
    environment:
      DJANGO_SETTINGS_MODULE: "core.settings"
      PYTHONPATH: /app
    command: celery -A apps.tasks worker -l info
    depends_on:
      redis:
        condition: service_healthy
    restart: always

  askanalytics-beat:
    image: your-registry-url/askanalytics-worker:latest
    env_file: ".env"
    networks:
      - db_network
    environment:
      DJANGO_SETTINGS_MODULE: "core.settings"
      PYTHONPATH: /app
    command: celery -A apps.tasks beat -l info
    depends_on:
      redis:
        condition: service_healthy
    restart: always

volumes:
  redis_data:

networks:
  db_network:
    driver: bridge
  web_network:
    driver: bridge
```

## 4. Monitoring and Maintenance

### 4.1. Health Checks
- Implement health check endpoints for all services
- Configure Docker health checks for automatic recovery
- Set up external monitoring for service availability

### 4.2. Logging
- Centralize logs from all containers
- Implement structured logging for easier analysis
- Configure log rotation to prevent disk space issues

### 4.3. Backup Strategy
- Regular database backups
- Redis persistence configuration
- Backup of environment configuration

## 5. Scaling Considerations

### 5.1. Horizontal Scaling
- Scale application containers based on load
- Configure Celery workers for different task types
- Implement Redis clustering for high availability

### 5.2. Resource Management
- Set appropriate resource limits for containers
- Monitor resource usage and adjust as needed
- Implement auto-scaling based on metrics

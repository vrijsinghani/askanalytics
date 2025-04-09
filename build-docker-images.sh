#!/bin/bash
set -e  # Exit immediately if a command exits with a non-zero status

# Configuration
REGISTRY=${DOCKER_REGISTRY:-"registry.rijsinghani.us"}
PROJECT=${DOCKER_PROJECT:-"askanalytics"}
VERSION=$(git describe --tags --always --dirty || echo "latest")
COMMIT=$(git rev-parse --short HEAD || echo "unknown")
COMMIT_DATE=$(git show -s --format=%ct HEAD || echo $(date +%s))

echo "Building Docker images for $PROJECT version: $VERSION (commit: $COMMIT, date: $COMMIT_DATE)"

# Ensure requirements.txt is up to date
echo "Updating requirements.txt..."
source .venv/bin/activate
uv pip freeze > requirements.docker.txt
deactivate

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

# Note: Redis uses the official Redis image, so we don't need to build it
PUSH_IMAGES=true
# Push images to registry if PUSH_IMAGES is set to true
if [ "${PUSH_IMAGES:-false}" = "true" ]; then
    echo "Pushing images to registry..."
    docker push "$REGISTRY/$PROJECT:$VERSION"
    docker push "$REGISTRY/$PROJECT:latest"
    docker push "$REGISTRY/$PROJECT-worker:$VERSION"
    docker push "$REGISTRY/$PROJECT-worker:latest"

    # Clean up old images
    echo "Cleaning up old images..."
    docker system prune -f
fi

echo "Docker build completed successfully!"

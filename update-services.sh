#!/bin/bash
set -e

# Configuration
COMPOSE_FILE=${COMPOSE_FILE:-"docker-compose.yml"}
ENV_FILE=${ENV_FILE:-".env"}

# Check if the compose file exists
if [ ! -f "$COMPOSE_FILE" ]; then
    echo "Error: Compose file $COMPOSE_FILE not found!"
    exit 1
fi

# Check if the environment file exists
if [ ! -f "$ENV_FILE" ]; then
    echo "Warning: Environment file $ENV_FILE not found. Using default environment variables."
fi

echo "Pulling latest images..."
docker-compose -f $COMPOSE_FILE pull

echo "Updating services..."
docker-compose -f $COMPOSE_FILE up -d

echo "Verifying update..."
docker-compose -f $COMPOSE_FILE ps

echo "Cleaning up old images..."
docker image prune -f

echo "Update completed successfully!"

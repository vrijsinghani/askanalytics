# Docker Swarm Deployment Guide

This guide explains how to deploy the AskAnalytics application using Docker Swarm with Portainer.

## Prerequisites

- Docker Swarm cluster set up
- Portainer installed on the Swarm cluster
- Access to a MinIO server (configured in your .env file)
- Access to a PostgreSQL database (configured in your .env file)

## Configuration Files

- `docker-compose.yml` - Standard Docker Compose file for local development
- `docker-compose.swarm.yml` - Optimized for Docker Swarm deployment

## Environment Variables

Ensure your `.env` file contains all necessary configuration, including:

```
# Database settings
DB_ENGINE=postgresql
DB_NAME=askanalytics
DB_USERNAME=postgres
DB_PASS=your-db-password
DB_HOST=your-db-host
DB_PORT=5432

# Redis settings
REDIS_HOST=redis
REDIS_PORT=6379

# MinIO settings
STORAGE_BACKEND=MINIO
MINIO_ACCESS_KEY=your-access-key
MINIO_SECRET_KEY=your-secret-key
MINIO_BUCKET_NAME=askanalytics
MINIO_ENDPOINT=https://minio.example.com
MINIO_USE_SSL=True
MINIO_VERIFY_SSL=True
MINIO_MAX_CONNECTIONS=30
```

## Deployment Steps

### Using Portainer

1. Log in to your Portainer instance
2. Navigate to "Stacks" and click "Add stack"
3. Give your stack a name (e.g., "askanalytics")
4. Upload the `docker-compose.swarm.yml` file or paste its contents
5. Click "Deploy the stack"

### Using Docker CLI

If you prefer using the Docker CLI:

```bash
# Deploy the stack
docker stack deploy -c docker-compose.swarm.yml askanalytics

# Check stack status
docker stack services askanalytics

# Scale a service
docker service scale askanalytics_askanalytics=2
```

## Security Considerations

For production deployments, consider using Docker secrets instead of environment variables for sensitive information:

1. Create secrets in Docker Swarm:
```bash
echo "your-access-key" | docker secret create minio_access_key -
echo "your-secret-key" | docker secret create minio_secret_key -
```

2. Modify the docker-compose.swarm.yml file to use these secrets:
```yaml
services:
  askanalytics:
    secrets:
      - minio_access_key
      - minio_secret_key
    environment:
      - MINIO_ACCESS_KEY_FILE=/run/secrets/minio_access_key
      - MINIO_SECRET_KEY_FILE=/run/secrets/minio_secret_key

secrets:
  minio_access_key:
    external: true
  minio_secret_key:
    external: true
```

## Monitoring

- Health checks are configured for all services
- Access the health check endpoint at `/health/` for detailed status
- Use `/health/?format=simple` for a simple "OK" response

## Scaling

The application is designed to scale horizontally. You can increase the number of replicas for the askanalytics service:

```bash
docker service scale askanalytics_askanalytics=3
```

Note that the Celery beat service should always have exactly one replica to avoid scheduling duplicate tasks.

## Troubleshooting

- Check service logs: `docker service logs askanalytics_askanalytics`
- Verify health status: `curl http://your-app-url/health/`
- Check if MinIO is accessible from the containers

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
5. **IMPORTANT**: Before deploying, go to the "Environment variables" tab
6. Click "Load variables from .env file" and upload your `.env` file
7. Verify that all environment variables are loaded correctly
8. Click "Deploy the stack"

**Note**: The stack file uses YAML anchors (`&common-env`) to define environment variables once and reuse them across all services. This ensures consistency and makes maintenance easier. All variables from your `.env` file are included in this common definition.

**Important**: When using YAML anchors with the `<<: *common-env` syntax, be careful not to define an `environment` section after it, as this will completely override the common environment variables rather than merging with them.

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

### Environment Variables Issues

#### Common Issue: Environment Variables Not Being Passed

If you're seeing errors like "no such table: django_celery_beat_periodictask" in the Celery Beat container, it's likely that the environment variables (especially database connection details) aren't being passed correctly.

This often happens when you define an `environment` section after using the `<<: *common-env` anchor, which completely overrides the common environment variables rather than merging with them.

**Solution**: Either move all environment variables to the common section or ensure you don't redefine the `environment` key after using the anchor.

#### Understanding YAML Anchors in the Stack File

The stack file uses YAML anchors to define environment variables once and reuse them:

```yaml
# Define common environment variables
x-common-env: &common-env
  environment:
    - DB_HOST=${DB_HOST}
    # ... other variables

services:
  askanalytics:
    # Use the common environment variables
    <<: *common-env
    # Service-specific settings
```

This approach ensures all services have the same environment variables without duplication.

#### Troubleshooting Missing Environment Variables

If you're seeing errors like "Attempting to connect to database at : with user" or other missing environment variable issues:

1. **Check Portainer Environment Variables**:
   - In Portainer, go to your stack
   - Click on "Environment variables"
   - Verify all variables are present and correctly formatted

2. **Manually Add Critical Variables**:
   - If specific variables aren't being passed, add them directly in the Portainer UI
   - Focus on database connection variables: `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USERNAME`, `DB_PASS`

3. **Check Container Logs**:
   - Look for specific error messages about missing environment variables
   - The entrypoint script will print environment variable values for debugging

### Database Connection Issues

If you're seeing database connection errors:

1. **Verify Database Accessibility**:
   - Make sure your database server allows connections from the Swarm nodes
   - Check firewall rules and network connectivity

2. **Test Connection Manually**:
   - Connect to a container: `docker exec -it <container_id> bash`
   - Try to connect to the database: `python -c "import psycopg2; conn = psycopg2.connect('host=<db_host> port=<db_port> dbname=<db_name> user=<db_user> password=<db_pass>'); print('Connected!')"`

### General Troubleshooting

- Check service logs: `docker service logs askanalytics_askanalytics`
- Verify health status: `curl http://your-app-url/health/`
- Check if MinIO is accessible from the containers
- Inspect container environment: `docker exec <container_id> env`

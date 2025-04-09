#!/bin/bash
set -e

# Wait for database to be ready (optional but recommended)
if [ "$WAIT_FOR_DB" = "true" ]; then
    echo "Waiting for database to be ready..."
    echo "Attempting to connect to database at ${DB_HOST}:${DB_PORT} with user ${DB_USERNAME}"

    # Run the database check script
    python /app/check_db.py
    if [ $? -ne 0 ]; then
        echo "Database connection failed. Exiting."
        exit 1
    fi
fi

# Wait for Redis to be ready
if [ "$WAIT_FOR_REDIS" = "true" ]; then
    echo "Waiting for Redis to be ready..."

    # Run the Redis check script
    python /app/check_redis.py
    if [ $? -ne 0 ]; then
        echo "Redis connection failed. Exiting."
        exit 1
    fi
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

# Create superuser if requested
if [ "$CREATE_SUPERUSER" = "true" ] && [ -n "$DJANGO_SUPERUSER_EMAIL" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
    echo "Creating/updating superuser..."
    python manage.py createsuperuser --noinput || echo "Superuser already exists."
fi

# Execute the main command
echo "Starting application..."
exec "$@"

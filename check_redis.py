#!/usr/bin/env python3
import sys
import time
import socket
import redis
from os import environ

# Get Redis connection parameters
host = environ.get('REDIS_HOST')
port = environ.get('REDIS_PORT')

# Print environment variables for debugging
print(f'Redis environment variables:')
print(f'REDIS_HOST: {host}')
print(f'REDIS_PORT: {port}')

# Set defaults if not provided
if not host:
    print('WARNING: REDIS_HOST not set, defaulting to localhost')
    host = 'localhost'
if not port:
    print('WARNING: REDIS_PORT not set, defaulting to 6379')
    port = '6379'

# Try to resolve the hostname
try:
    print(f'Resolving Redis hostname {host}...')
    ip = socket.gethostbyname(host)
    print(f'Resolved {host} to {ip}')
except socket.gaierror as e:
    print(f'WARNING: Could not resolve Redis hostname {host}: {e}')

print(f'Connecting to Redis at {host}:{port}')

for i in range(30):
    try:
        print(f'Attempt {i+1}/30: Connecting to Redis at {host}:{port}')
        r = redis.Redis(host=host, port=port, socket_connect_timeout=5)
        r.ping()
        print('Redis is ready!')
        sys.exit(0)
    except (redis.exceptions.ConnectionError, redis.exceptions.TimeoutError) as e:
        print(f'Redis not ready yet. Error: {e}')
        time.sleep(5)

print('Could not connect to Redis after 30 attempts. Exiting.')
sys.exit(1)

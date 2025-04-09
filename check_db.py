#!/usr/bin/env python3
import sys
import time
import socket
import psycopg2
from os import environ

# Get database connection parameters
host = environ.get('DB_HOST')
port = environ.get('DB_PORT')
dbname = environ.get('DB_NAME')
user = environ.get('DB_USERNAME')
password = environ.get('DB_PASS')

# Print environment variables for debugging
print(f'Environment variables:')
print(f'DB_HOST: {host}')
print(f'DB_PORT: {port}')
print(f'DB_NAME: {dbname}')
print(f'DB_USERNAME: {user}')
print(f'DB_PASS: {"*****" if password else "<not set>"}')

# Set defaults if not provided
if not host:
    print('WARNING: DB_HOST not set, defaulting to localhost')
    host = 'localhost'
if not port:
    print('WARNING: DB_PORT not set, defaulting to 5432')
    port = '5432'
if not dbname:
    print('WARNING: DB_NAME not set, defaulting to postgres')
    dbname = 'postgres'
if not user:
    print('WARNING: DB_USERNAME not set, defaulting to postgres')
    user = 'postgres'

# Try to resolve the hostname
try:
    print(f'Resolving hostname {host}...')
    ip = socket.gethostbyname(host)
    print(f'Resolved {host} to {ip}')
except socket.gaierror as e:
    print(f'WARNING: Could not resolve hostname {host}: {e}')

print(f'Connecting to PostgreSQL at {host}:{port}, database: {dbname}, user: {user}')

for i in range(60):  # 60 attempts with 5 second delay = 5 minutes total
    try:
        # Explicitly specify connection parameters
        conn_string = f'host={host} port={port} dbname={dbname} user={user} password={password}'
        masked_conn_string = conn_string.replace(password, "*****" if password else "<not set>")
        print(f'Attempt {i+1}/60: Connecting with: {masked_conn_string}')
        
        conn = psycopg2.connect(conn_string)
        conn.close()
        print('Database is ready!')
        sys.exit(0)
    except psycopg2.OperationalError as e:
        print(f'Database not ready yet. Error: {e}')
        time.sleep(5)

print('Could not connect to database after 60 attempts. Exiting.')
sys.exit(1)

#!/bin/bash

# Start Redis with password
redis-server /etc/redis/redis.conf &

# Wait for Redis to fully start (adjust sleep time as needed)
sleep 10

# Start FastAPI application
uvicorn main:app --host 0.0.0.0 --port 8000

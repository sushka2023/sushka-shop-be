#!/bin/bash

# Activate virtual environment
#source /root/.cache/pypoetry/virtualenvs/store-2fuo_mI6-py3.10/bin/activate

# Start Redis with password
redis-server /etc/redis/redis.conf &

# Wait for Redis to fully start (adjust sleep time as needed)
sleep 10

# Start FastAPI application
uvicorn main:app --host 0.0.0.0 --port 8000

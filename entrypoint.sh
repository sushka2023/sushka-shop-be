#!/bin/bash

poetry shell

# Запускаємо Redis з паролем
redis-server /etc/redis/redis.conf &

# Запускаємо FastAPI
uvicorn main:app --host 0.0.0.0 --port 8000
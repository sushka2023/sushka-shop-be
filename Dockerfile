# Використовуємо офіційний образ Python
FROM python:3.10.11

# Встановлюємо залежності Python
COPY requirements.txt /app/
WORKDIR /app
RUN pip install --no-cache-dir -r requirements.txt

# Встановлюємо Git
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Клонуємо репозиторій з GitHub
RUN git clone https://github.com/sushka2023/sushka-shop-be /app_backend
WORKDIR /app_backend
RUN git checkout feature/caching_in_redis

# Встановлюємо Redis
RUN apt-get update && apt-get install -y redis-server && rm -rf /var/lib/apt/lists/*

# Налаштовуємо Redis ($REDIS_PASSWORD із .env)
RUN sed -i 's/bind 127.0.0.1/bind 0.0.0.0/' /etc/redis/redis.conf
RUN echo "requirepass $REDIS_PASSWORD" >> /etc/redis/redis.conf
RUN echo "notify-keyspace-events Ex" >> /etc/redis/redis.conf

# Відкриваємо порт для FastAPI
EXPOSE 8000

# Запускаємо entrypoint скрипт
RUN chmod +x /app_backend/entrypoint.sh
ENTRYPOINT ["/app_backend/entrypoint.sh"]
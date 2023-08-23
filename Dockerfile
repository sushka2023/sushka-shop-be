# Використовуємо офіційний образ Python
FROM ubuntu:latest

# Встановлюємо залежності Python
#COPY requirements.txt /app_backend
#WORKDIR /app_backend
#RUN pip install --no-cache-dir -r requirements.txt

# Встановлюємо Git
RUN apt-get update && apt-get install -y git  \
    && apt-get install -y python3-pip

RUN pip install poetry

# Клонуємо репозиторій з GitHub
RUN git clone https://github.com/sushka2023/sushka-shop-be /app_backend
WORKDIR /app_backend
RUN git checkout feature/caching_in_redis
WORKDIR /app_backend/sushka-shop-be

# Встановлюємо Redis
RUN apt-get update && apt-get install -y redis-server && rm -rf /var/lib/apt/lists/*

# Налаштовуємо Redis ($REDIS_PASSWORD із .env)
RUN sed -i 's/bind 127.0.0.1/bind 0.0.0.0/' /etc/redis/redis.conf
RUN echo "requirepass $REDIS_PASSWORD" >> /etc/redis/redis.conf
RUN echo "notify-keyspace-events Ex" >> /etc/redis/redis.conf

#RUN pip install --no-cache-dir -r requirements.txt
RUN poetry lock
RUN poetry install
#RUN poetry shell -n

# Відкриваємо порт для FastAPI
EXPOSE 8000

# Запускаємо entrypoint скрипт
RUN chmod +x /app_backend/entrypoint.sh
ENTRYPOINT ["/app_backend/entrypoint.sh"]
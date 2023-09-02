# Використовуємо офіційний образ Redis з підтримкою альпійського Linux
#FROM redis:latest

# Встановлюємо non-root користувача та групу для Redis
#RUN addgroup -S redisuser && adduser -S redisuser -G redisuser

# Встановлюємо деякі додаткові пакети для налаштування безпеки (необов'язково)
#RUN apk --no-cache add acl

# Копіюємо конфігураційний файл Redis із локальної директорії в образ
#COPY redis/redis.conf /usr/local/etc/redis/redis.conf

# Змінюємо власника та групу файлу конфігурації на non-root користувача та групу
#RUN chown redisuser:redisuser /usr/local/etc/redis/redis.conf

# Передача пароля з змінної середовища до конфігураційного файлу Redis
#RUN echo "requirepass \"\$REDIS_PASSWORD\"" >> /usr/local/etc/redis/redis.conf

# Вказуємо Redis використовувати наш конфігураційний файл
#CMD ["redis-server", "/usr/local/etc/redis/redis.conf"]
#CMD ["redis-server"]

# Вказуємо порт, на якому працюватиме Redis (за замовчуванням 6379)
#EXPOSE 6379


# Використовуємо офіційний образ Redis з Docker Hub
#FROM redis:latest

# Створюємо папку для файлу конфігурації Redis
#RUN mkdir -p /usr/local/etc/redis/

# Створюємо файл конфігурації Redis всередині контейнера
#RUN echo "bind 0.0.0.0" > /usr/local/etc/redis/redis.conf \
#    && echo "port 6379" >> /usr/local/etc/redis/redis.conf \
#    && echo "maxmemory 100mb" >> /usr/local/etc/redis/redis.conf \
#    && echo "maxmemory-policy allkeys-lru" >> /usr/local/etc/redis/redis.conf

# Запускаємо Redis з використанням нашого файлу конфігурації
#CMD ["redis-server", "/usr/local/etc/redis/redis.conf"]

# Використовуємо офіційний образ Python з Docker Hub
FROM python:3.10.11

# Встановлюємо додаткові пакети або бібліотеки (якщо потрібно)
RUN apt-get update -y && apt-get upgrade -y && apt install nano iproute2 telnet git -y

# Створюємо папку для проекту
RUN mkdir -p /app

# Клонуємо репозиторій з GitHub (замініть URL на URL вашого репозиторію)
RUN git clone https://github.com/sushka2023/sushka-shop-be /app

# Переходимо в каталог з клонованим репозиторієм
WORKDIR /app

# Переключаємося на певну гілку (замініть 'yourbranch' на назву гілки)
RUN git checkout redis_dockerfile

# Встановлюємо залежності з requirements.txt
RUN pip install -r requirements.txt

# Встановлюємо Redis
RUN apt install redis-server -y

# Створюємо папку для файлу конфігурації Redis
RUN mkdir -p /usr/local/etc/redis/

# Створюємо файл конфігурації Redis всередині контейнера
RUN echo "bind 127.0.0.1" > /usr/local/etc/redis/redis.conf \
    && echo "port 6379" >> /usr/local/etc/redis/redis.conf \
    && echo "maxmemory 100mb" >> /usr/local/etc/redis/redis.conf \
    && echo "maxmemory-policy allkeys-lru" >> /usr/local/etc/redis/redis.conf

# Змінні оточення
ENV DATABASE_URL="${DATABASE_URL}"

ENV SECRET_KEY="${SECRET_KEY}"
ENV ALGORITHM="${ALGORITHM}"

ENV MAIL_USERNAME="${MAIL_USERNAME}"
ENV MAIL_PASSWORD="${MAIL_PASSWORD}"
ENV MAIL_FROM="${MAIL_FROM}"
ENV MAIL_PORT="${MAIL_PORT}"
ENV MAIL_SERVER="${MAIL_SERVER}"
ENV MAIL_FROM_NAME="${MAIL_FROM_NAME}"

ENV REDIS_HOST="${REDIS_HOST}"
ENV REDIS_PORT="${REDIS_PORT}"
ENV REDIS_PASSWORD="${REDIS_PASSWORD}"

EXPOSE 8000
# Запускаємо Redis з використанням нашого файлу конфігурації
CMD ["redis-server", "/usr/local/etc/redis/redis.conf"]

# Запускаємо FastAPI додаток за допомогою uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
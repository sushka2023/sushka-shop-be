# Використовуємо офіційний образ Python з Docker Hub
FROM python:3.10.11

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

ENV SENTRY_URL="${SENTRY_URL}"
ENV SENTRY_SECRET_KEY="${SENTRY_SECRET_KEY}"
ENV SENTRY_POSTGRES_HOST="${SENTRY_POSTGRES_HOST}"
ENV SENTRY_POSTGRES_PORT="${SENTRY_POSTGRES_PORT}"
ENV SENTRY_DB_NAME="${SENTRY_DB_NAME}"
ENV SENTRY_DB_USER="${SENTRY_DB_USER}"
ENV SENTRY_DB_PASSWORD="${SENTRY_DB_PASSWORD}"
ENV SENTRY_REDIS_HOST="${SENTRY_REDIS_HOST}"

# Встановлюємо додаткові пакети або бібліотеки (якщо потрібно)
RUN apt-get update -y && apt-get upgrade -y && apt install nano iproute2 telnet git -y

# Створюємо папку для проекту
RUN mkdir -p /app

# Клонуємо репозиторій з GitHub (замініть URL на URL вашого репозиторію)
RUN git clone https://github.com/sushka2023/sushka-shop-be /app

# Переходимо в каталог з клонованим репозиторієм
WORKDIR /app

# Переключаємося на певну гілку (замініть 'yourbranch' на назву гілки)
RUN git checkout master


RUN apt-get update -y && apt-get install -y libpq-dev

# RUN pip install psycopg2-binary



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

# Port
EXPOSE 8000

# Встановлюємо supervisord
RUN apt install supervisor -y

# Копіюємо конфігураційний файл supervisord.conf
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Встановлюємо ENTRYPOINT для supervisord в якому запускаємо Fastapi and Redis
#ENTRYPOINT ["/usr/bin/supervisord", "-n", "-c", "/etc/supervisor/conf.d/supervisord.conf"]

# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

# Встановлюємо ENTRYPOINT для запуску лише FastAPI
# ENTRYPOINT ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
# CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port 8000 & sleep 10 && alembic upgrade head && tail -f /dev/null"]

CMD ["sh", "-c", "alembic upgrade head && uvicorn main:app --host 0.0.0.0 --port 8000"]


# CMD ["sh", "-c", "alembic upgrade head && tail -f /dev/null"]

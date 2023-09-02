# Використовуємо офіційний образ Redis з підтримкою альпійського Linux
FROM redis:latest

# Встановлюємо non-root користувача та групу для Redis
#RUN addgroup -S redisuser && adduser -S redisuser -G redisuser

# Встановлюємо деякі додаткові пакети для налаштування безпеки (необов'язково)
#RUN apk --no-cache add acl

# Копіюємо конфігураційний файл Redis із локальної директорії в образ
COPY redis/redis.conf /usr/local/etc/redis/redis.conf

# Змінюємо власника та групу файлу конфігурації на non-root користувача та групу
#RUN chown redisuser:redisuser /usr/local/etc/redis/redis.conf

# Передача пароля з змінної середовища до конфігураційного файлу Redis
#RUN echo "requirepass \"\$REDIS_PASSWORD\"" >> /usr/local/etc/redis/redis.conf

# Вказуємо Redis використовувати наш конфігураційний файл
CMD ["redis-server", "/usr/local/etc/redis/redis.conf"]
#CMD ["redis-server"]

# Вказуємо порт, на якому працюватиме Redis (за замовчуванням 6379)
EXPOSE 6379
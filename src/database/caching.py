from contextlib import contextmanager

import redis
from redis.exceptions import AuthenticationError
from src.conf.config import settings


@contextmanager
def get_redis():
    redis_client = redis.Redis(
        host=settings.redis_host,
        port=settings.redis_port,
        db=0,
        password=settings.redis_password
    )
    try:
        redis_client.ping()  # Перевірка підключення
        yield redis_client
    except redis.exceptions.AuthenticationError as error:
        print(f'Authentication failed to connect to Redis: {error}')
    except Exception as error:
        print(f'Unable to connect to Redis: {error}')
    finally:
        redis_client.connection_pool.disconnect()

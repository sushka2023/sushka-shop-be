import redis
from redis.exceptions import AuthenticationError
from src.conf.config import settings


def get_redis():
    try:
        redis_client = redis.Redis(
            host=settings.redis_host,
            port=settings.redis_port,
            db=0,
            password=settings.redis_password
            )

    except AuthenticationError as error:
        redis_client = None
        print(f'Authentication failed to connect to redis\n{error}')
        # TODO loger

    except Exception as error:
        redis_client = None
        print(f'Unable to connect to redis\n{error}')
        # TODO loger

    return redis_client if redis_client else None


redis_cl = get_redis()

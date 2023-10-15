from src.database.caching import get_redis


async def delete_cache_in_redis():
    # Redis client
    redis_client = get_redis()
    # Delete cache in redis
    redis_client.flushdb()


from config.config import get_redis_client


class RedisEvents:
    def __init__(self):
        self.redis_client = get_redis_client()

    def save_redis(self, key, value, ex=None):
        self.redis_client.set(key, value, ex=ex)

    def get_redis(self, key):
        return self.redis_client.get(key)
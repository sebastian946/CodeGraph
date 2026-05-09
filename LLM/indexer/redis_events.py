
from LLM.config.config import get_redis_client


class RedisEvents:
    def __init__(self):
        self.redis_client = get_redis_client(self)

    def save_redis(self, key, value):
        self.redis_client.set(key, value)
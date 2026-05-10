from cryptography.fernet import Fernet
from config.config import get_redis_client, get_settings


class RedisEvents:
    def __init__(self):
        self.redis_client = get_redis_client()
        self._fernet = Fernet(get_settings().FERNET_KEY.encode())

    def save_redis(self, key: str, value: str, ex: int | None = None) -> None:
        self.redis_client.set(key, value, ex=ex)

    def get_redis(self, key: str) -> str | None:
        value: bytes | None = self.redis_client.get(key)  # type: ignore[assignment]
        return value.decode() if value else None

    def save_encrypted(self, key: str, value: str, ex: int | None = None) -> None:
        encrypted = self._fernet.encrypt(value.encode())
        self.redis_client.set(key, encrypted, ex=ex)

    def get_decrypted(self, key: str) -> str | None:
        raw: bytes | None = self.redis_client.get(key)  # type: ignore[assignment]
        if not raw:
            return None
        return self._fernet.decrypt(raw).decode()

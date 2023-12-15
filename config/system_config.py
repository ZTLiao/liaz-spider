from config.redis_config import RedisConfig


class SystemConfig:
    def __init__(self, redis: RedisConfig):
        self.redis = redis

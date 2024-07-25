from flask_caching import Cache

cache = Cache(config={
    "CACHE_TYPE": "RedisCache", 
    "CACHE_DEFAULT_TIMEOUT": 300,
    "CACHE_REDIS_HOST": "localhost",
    "CACHE_REDIS_PORT": 6379
})

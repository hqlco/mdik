import redis
from fastapi import HTTPException
from datetime import timedelta
from dotenv import load_dotenv
import os

load_dotenv()

redis_client = redis.StrictRedis(host=os.getenv("REDIS_HOST"), port=6379, db=0, password=os.getenv("REDIS_PASSWORD"), decode_responses=False)

CACHE_TIMEOUT = timedelta(minutes=10)

def get_cache(key: str):
    try:
        return redis_client.get(key)
    except redis.RedisError as e:
        raise HTTPException(status_code=500, detail=f"Redis Error: {str(e)}")

def set_cache(key: str, value: str, timeout: timedelta = CACHE_TIMEOUT):
    try:
        redis_client.setex(key, timeout, value)
    except redis.RedisError as e:
        raise HTTPException(status_code=500, detail=f"Redis Error: {str(e)}")

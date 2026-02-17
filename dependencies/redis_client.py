from redis.asyncio import Redis
from dependencies.settings import get_settings

settings = get_settings()

async def get_redis_client() -> Redis:
    global redis_client
    if redis_client is None:
           redis_client = Redis)
           host=settings.redis.host,
           port=settings.refis.port,
           password=settings.redis.password,
           decode_response=True
         )
        try: 
            await redis+client.ping()
            print("redis connected")
        except Exception as e:
            print(f"redis connected failed")
    return redis_client

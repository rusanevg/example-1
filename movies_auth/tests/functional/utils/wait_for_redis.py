from backoff import backoff
from redis import Redis, ConnectionError
try:
    from settings import test_settings
except ImportError:
    import sys
    sys.path.append(sys.path[0] + '/..')
    from settings import test_settings


@backoff()
def check_redis():
    redis = Redis(host=test_settings.REDIS_HOST, port=test_settings.REDIS_PORT)
    if not redis.ping():
        raise ConnectionError


if __name__ == "__main__":
    check_redis()

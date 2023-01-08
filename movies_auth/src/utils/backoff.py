import sys
import time
import logging
from functools import wraps
from datetime import datetime


def backoff(start_sleep_time=0.1, factor=2, border_sleep_time=30, max_retries=10):
    def func_wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):
            sleep = start_sleep_time
            retries = 0
            while True:
                try:
                    return func(*args, **kwargs)
                except Exception:
                    if retries > max_retries:
                        print(f"{datetime.now()} {func.__name__} Превышено максимальное кол-во попыток")
                        logging.info(
                            f"{datetime.now()} Превышено максимальное кол-во попыток"
                        )
                        # Выход из скрипта с сообщением об ошибке. Используется чтобы предотвратить запуск тестов
                        sys.exit(1)
                    else:
                        time.sleep(sleep)
                        if sleep < border_sleep_time / factor:
                            sleep = start_sleep_time * (factor ** retries)
                        else:
                            sleep = border_sleep_time
                        retries += 1
        return inner
    return func_wrapper

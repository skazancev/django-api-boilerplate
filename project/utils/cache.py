import functools
from datetime import timedelta, datetime


def custom_lru_cache(seconds: int, *cache_args, **cache_kwargs):
    def wrapper_cache(func):
        func = functools.lru_cache(*cache_args, **cache_kwargs)(func)
        func.delta = timedelta(seconds=seconds)
        func.expiration = datetime.utcnow() + func.delta

        @functools.wraps(func)
        def wrapped_func(*args, **kwargs):
            if datetime.utcnow() >= func.expiration:
                func.cache_clear()
                func.expiration = datetime.utcnow() + func.delta

            return func(*args, **kwargs)

        return wrapped_func

    return wrapper_cache

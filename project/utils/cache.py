import pprint
from asgiref.local import Local as LocalContext

import hashlib

import functools
from datetime import timedelta, datetime

from django.core.cache import cache as django_cache

from utils.core import rgetattr


def build_cache_key(*args, **kwargs):
    if args or kwargs:
        return hashlib.md5(pprint.pformat({'args': args, **kwargs}).encode()).hexdigest()
    return 'empty'


class LocalContextCache:
    context = LocalContext()

    @classmethod
    def set(cls, key, value, **kwargs):
        setattr(cls.context, key, value)

    @classmethod
    def get(cls, key, use_rgetattr=False):
        if use_rgetattr:
            return rgetattr(cls.context, key, None)
        return getattr(cls.context, key, None)


local_context_cache = LocalContextCache


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


def cached_method(func):
    def wrap(self, *args, **kwargs):
        args_key = build_cache_key(*args, **kwargs)
        key = f'_cached_{func.__name__}_{args_key}'
        if not hasattr(self, key):
            setattr(self, key, func(self, *args, **kwargs))
        return getattr(self, key)
    return wrap


def cached_function(timeout, cache_key=None):
    def decorator(func):
        def wrap(*args, reset_cache=False, **kwargs):
            if timeout == 'local':
                cache = local_context_cache
            else:
                cache = django_cache

            key = cache_key or f'{func.__name__}_{build_cache_key(*args, **kwargs)}'
            if callable(key):
                key = key(*args, **kwargs)
            if not reset_cache and (value := cache.get(key)):
                return value

            value = func(*args, **kwargs)
            cache.set(key, value, timeout=timeout)
            return value

        return wrap

    return decorator

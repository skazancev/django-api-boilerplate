from django.utils.deprecation import MiddlewareMixin

from utils.cache import local_context_cache


class CoreMiddleware(MiddlewareMixin):
    def process_request(self, request):
        local_context_cache.set('request', request)

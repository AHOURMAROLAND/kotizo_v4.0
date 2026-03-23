import time
import logging
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger('kotizo')

class PerformanceMiddleware(MiddlewareMixin):
    def process_request(self, request):
        request.start_time = time.time()

    def process_response(self, request, response):
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time
            if duration > 2.0:
                logger.warning(f'Slow request: {request.path} took {duration:.2f}s')
        return response
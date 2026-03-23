from functools import wraps
from rest_framework.response import Response
from rest_framework import status

def require_verified(func):
    @wraps(func)
    def wrapper(self, request, *args, **kwargs):
        if not request.user.est_verifie:
            return Response(
                {'error': 'Compte non vérifié. Veuillez vérifier votre identité.'},
                status=status.HTTP_403_FORBIDDEN
            )
        return func(self, request, *args, **kwargs)
    return wrapper

def require_active(func):
    @wraps(func)
    def wrapper(self, request, *args, **kwargs):
        if request.user.est_bloque:
            return Response(
                {'error': 'Compte bloqué. Contactez le support.'},
                status=status.HTTP_403_FORBIDDEN
            )
        return func(self, request, *args, **kwargs)
    return wrapper
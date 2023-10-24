from django.utils.deprecation import MiddlewareMixin
from usuarios.models import *

class ProfissionalMiddleware(MiddlewareMixin):
    def process_request(self, request):
        request.is_profissional = hasattr(request.user, 'profissional')
        request.is_clinica = hasattr(request.user, 'clinica')
        request.is_cliente = hasattr(request.user, 'cliente')
        if hasattr(request.user, 'profissional'):
            request.profissional = request.user.profissional
        
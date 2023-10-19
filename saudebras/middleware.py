from django.utils.deprecation import MiddlewareMixin

class ProfissionalMiddleware(MiddlewareMixin):
    def process_request(self, request):
        request.is_profissional = hasattr(request.user, 'profissional')
        request.is_clinica = hasattr(request.user, 'clinica')

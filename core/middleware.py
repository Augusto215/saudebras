from django.shortcuts import render
from django.http import Http404
from django.core.exceptions import PermissionDenied
from django.urls import resolve, Resolver404
import logging

logger = logging.getLogger(__name__)

class ErrorHandlingMiddleware:
    """
    Middleware personalizado para lidar com erros e redirecionar 
    para páginas de erro personalizadas apenas quando necessário
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Só interferir se a resposta for um erro
        if response.status_code == 404:
            try:
                # Verificar se é realmente uma URL inválida
                resolve(request.path_info)
            except Resolver404:
                # URL realmente não existe, mostrar página personalizada
                logger.warning(f"404 Error for URL: {request.path}")
                return render(request, '404.html', status=404)
        elif response.status_code == 403:
            logger.warning(f"403 Error for URL: {request.path}")
            return render(request, '403.html', status=403)
        elif response.status_code >= 500:
            logger.error(f"500 Error for URL: {request.path}")
            return render(request, '500.html', status=500)
            
        return response

    def process_exception(self, request, exception):
        """
        Processa exceções apenas para erros reais
        """
        try:
            if isinstance(exception, Http404):
                logger.warning(f"404 Exception for URL: {request.path}")
                return render(request, '404.html', status=404)
            elif isinstance(exception, PermissionDenied):
                logger.warning(f"403 Exception for URL: {request.path}")
                return render(request, '403.html', status=403)
            # Para outros erros críticos
            else:
                logger.error(f"500 Exception for URL: {request.path} - {str(exception)}")
                # Só retornar página de erro se DEBUG estiver False
                from django.conf import settings
                if not settings.DEBUG:
                    return render(request, '500.html', status=500)
        except Exception as e:
            logger.error(f"Error in middleware: {str(e)}")
            return None
        
        return None

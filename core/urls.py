from django.urls import path
from core.views import *
from django.conf import settings
from django.conf.urls.static import static
from .views import *

urlpatterns = [
    path('', home_view, name='home'),
    path('buscar_estados/', buscar_estados, name='buscar_estados'),
    path('profissionais/', listar_profissionais, name='listar_profissionais'),
    path('buscar_especialidades/', get_especialidades, name='buscar_especialidades'),
    path('get_states/', get_states, name='get_states'),
    path('get_cities/', get_cities, name='get_cities'),
    path('buscar_nomes/', buscar_nomes, name='buscar_nomes'),
    path('buscar_tipos/', buscar_tipos, name='buscar_tipos'),
    path('buscar_bairros/', buscar_bairros, name='buscar_bairros'),


    

    # Aqui estamos definindo a rota para a sua view home
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
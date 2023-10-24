from django.conf import settings
from django.conf.urls.static import static

from django.urls import path
from .views import *
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('registrarProfissional/', registerProfissional, name='registerProfissional'),
    path('registrarCliente/', registerCliente, name='registerCliente'),
    path('login/', user_login, name='login'),
    path('sair/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('registrarClinica/', registerClinica, name='registerClinica'),
    path('editar_perfil/', editar_perfil, name='editar_perfil'),
    path('editar_clinica/', editar_perfil_clinica, name='editar_clinica'),
    path('convenios_perfil', convenios_perfil, name='convenios_perfil'),
    path('alterar_profissional', alterar_Profissional, name='alterar_Profissional'),
    path('alterar_clinica', alterar_Clinica, name='alterar_clinica'),
    
    
    
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
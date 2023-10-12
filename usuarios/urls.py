from django.conf import settings
from django.conf.urls.static import static

from django.urls import path
from .views import *
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('registrarProfissional/', registerProfissional, name='registerProfissional'),
    path('registerCliente/', registerCliente, name='registerCliente'),
    path('login/', user_login, name='login'),
    path('sair/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('registrarClinica/', registerClinica, name='registerClinica'),
    path('editar_perfil/', editar_perfil, name='editar_perfil')
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
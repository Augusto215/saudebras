from django.urls import path
from .views import *
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('registerProfissional/', registerProfissional, name='registerProfissional'),
    path('registerCliente/', registerCliente, name='registerCliente'),
    path('login/', user_login, name='login'),
    path('sair/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    
]



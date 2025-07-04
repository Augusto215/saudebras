from django.urls import path
from core.views import *
from django.conf import settings
from django.conf.urls.static import static
from .views import *

urlpatterns = [
    path('', home_view, name='home'),
    path('buscar_estados/', buscar_estados, name='buscar_estados'),
    path('profissionais/', listar_profissionais, name='listar_profissionais'),
    path('clinicas/', listar_clinicas, name='listar_clinicas'),
    path('buscar_especialidades/', get_especialidades, name='buscar_especialidades'),
    path('get_states/', get_states, name='get_states'),
    path('get_cities/', get_cities, name='get_cities'),
    path('buscar_nomes/', buscar_nomes, name='buscar_nomes'),
    path('buscar_tipos/', buscar_tipos, name='buscar_tipos'),
    path('buscar_bairros/', buscar_bairros, name='buscar_bairros'),
    path('buscar_tipos_profissionais/', buscar_tipos_profissionais, name='buscar_tipos_profissionais'),
    path('buscar_tipos_clinicas/', buscar_tipos_clinicas, name='buscar_tipos_clinicas'),
    path('buscar_profissionais_por_tipo_clinica/',buscar_profissionais_por_tipo_clinica, name='buscar_profissionais_por_tipo_clinica' ),
    path('buscar_especialidades_por_tipo_clinica/', buscar_especialidades_por_tipo_clinica, name='buscar_especialidades_por_tipo_clinica'),
    path('buscar_estados_por_tipo_clinica/', buscar_estados_por_tipo_clinica, name='buscar_estados_por_tipo_clinica'),
    path('buscar_cidades_por_tipo_clinica/', buscar_cidades_por_tipo_clinica, name='buscar_cidades_por_tipo_clinica'),
    path('perfil/<int:profissional_id>/', perfil_profissional, name='perfil_profissional'),
    path('perfilClinica/<int:clinica_id>/', perfil_clinica, name='perfil_clinica' ),
    path('buscar_convenios_por_tipo_clinica/', buscar_convenios_por_tipo_clinica, name='uscar_convenios_por_tipo_clinica'),
    path('buscar_convenios_por_tipo_profissional/', buscar_convenios_por_tipo_profissional, name ="buscar_convenios_por_tipo_profissional"),
    path('pesquisar/<str:tipo_profissional>/', pesquisarProfissionais, name='pesquisarProfissionais'),
    path('pesquisarClinica/<str:tipo_clinica>/', pesquisarClinicas, name='pesquisarClinicas'),
    path('get_enderecos/', get_enderecos, name='get_enderecos'),
    path('get_enderecos_clinica/', get_enderecos_clinica, name='get_enderecos_clinica'),
    path('create-subscription/', create_subscription, name='create_subscription'),
    path('cancel-subscription', cancel_subscription_view, name='cancel-subscription'),
    path('success/', success_view, name='success'),
    path('cancel/', cancel_view, name='cancel'),
    path('stripe-webhook/', stripe_webhook, name='stripe_webhook'),
    path('sobre/', sobre, name='sobre'),
    path('vantagens/', vantagens, name='vantagens'),
    path('artigos/', artigos, name='artigos'),
    path('suporte/', suporte, name='suporte'),
    path('contato/', contato, name='contato'),
    path('create-payment-intent/',  create_payment_intent, name='create-payment-intent'),




    

    # Aqui estamos definindo a rota para a sua view home
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
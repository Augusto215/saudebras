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
    path('alterar_profissional/', alterar_Profissional, name='alterar_Profissional'),
    path('alterar_clinica', alterar_Clinica, name='alterar_Clinica'),
    path('sucesso', redirectCliente, name='sucessoCliente'),
    path('editar_cliente', editar_cliente, name='editar_cliente'),
    path('editar_senha/', editar_senha, name='editar_senha'),
    path('validate_password/', validate_password, name='validate_password'),
    
    # URLs administrativas para gestão de assinaturas
    path('admin/cleanup-subscriptions/', cleanup_invalid_subscriptions, name='cleanup_subscriptions'),
    path('admin/subscription-health/', check_subscription_health, name='subscription_health'),



# URL para a solicitação de redefinição de senha com formulário personalizado
path(
        'password_reset/',
        auth_views.PasswordResetView.as_view(
            form_class=EmailPasswordResetForm,
            html_email_template_name='registration/password_reset_email.html',  # Template para HTML
        ),
        name='password_reset'
    ),
    # Outras URLs do processo de redefinição de senha
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view( # Se você criou um formulário para esta etapa
        template_name='registration/password_reset_confirm.html'
    ), name='password_reset_confirm'),  
      path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/reset_done.html'), name='password_reset_complete'),
    
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
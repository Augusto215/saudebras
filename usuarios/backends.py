
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

class EmailOrCpfAuthenticationBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        User = get_user_model()

        try:
            # Verifica se o input é um e-mail
            validate_email(username)
            kwargs = {'email': username}
        except ValidationError:
            # Se não for e-mail, considera como CPF
            kwargs = {'username': username}

        try:
            # Tenta buscar o usuário por e-mail ou CPF
            user = User.objects.get(**kwargs)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None

class CaseInsensitiveModelBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        if username is None:
            username = kwargs.get(UserModel.USERNAME_FIELD)

        try:
            # Convertendo o username (e-mail) para minúsculas
            case_insensitive_username_field = '{}__iexact'.format(UserModel.USERNAME_FIELD)
            user = UserModel._default_manager.get(**{case_insensitive_username_field: username.lower()})
            if user.check_password(password) and self.user_can_authenticate(user):
                return user
        except UserModel.DoesNotExist:
            # Retorna None se não encontrar um usuário
            return None



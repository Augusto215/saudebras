from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
import uuid
from django import forms


TIPO_PROFISSIONAL_CHOICES = [
    ('medico', 'Médico'),
    ('dentista', 'Dentista'),
    # ... adicione outros tipos conforme necessário
]

ESPECIALIDADE_CHOICES = [
    ('cardiologista', 'Cardiologista'),
    ('ortopedista', 'Ortopedista'),
    # Adicione mais aqui
]




class CustomUserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError('O campo email é obrigatório')
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, username, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    nome = models.CharField(_('nome'), max_length=30, blank=True)
    sobrenome = models.CharField(_('sobrenome'), max_length=30, blank=True)
    email = models.EmailField(_('email address'), unique=True)
    username = models.CharField(_('cpf'), max_length=30, unique=True)
    telefone = models.CharField(_('telefone'), max_length=20, blank=True)
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)
    is_staff = models.BooleanField(_('staff status'), default=False)
    email_verification_token = models.UUIDField(default=uuid.uuid4, editable=False)
    email_verified = models.BooleanField(default=False)

    
    objects = CustomUserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name=_('groups'),
        blank=True,
        help_text=_('The groups this user belongs to. A user will get all permissions granted to each of their groups.'),
        related_name="customuser_groups",
        related_query_name="customuser",
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name=_('user permissions'),
        blank=True,
        help_text=_('Specific permissions for this user.'),
        related_name="customuser_user_permissions",
        related_query_name="customuser",
    )
    
class Especialidade(models.Model):
    nome = models.CharField(max_length=100)
    tipo_profissional = models.CharField(max_length=50, choices=TIPO_PROFISSIONAL_CHOICES, blank=True)

    def __str__(self):
        return self.nome
    
    
    
class Convenio(models.Model):
    nome = models.CharField(max_length=100)
    

    def __str__(self):
        return self.nome
    
    
class Idioma(models.Model):
    nome = models.CharField(max_length=100)
    

    def __str__(self):
        return self.nome


class Servico(models.Model):
    nome = models.CharField(max_length=100)
    

    def __str__(self):
        return self.nome


class Estado(models.Model):
    nome = models.CharField(max_length=100)
    
    def __str__(self):
        return self.nome

class Cidade(models.Model):
    estado = models.ForeignKey(Estado, related_name='cidades', on_delete=models.CASCADE)
    nome = models.CharField(max_length=100)
    
    def __str__(self):
        return self.nome



class Bairro(models.Model):
    nome = models.CharField(max_length=255)
    cidade = models.ForeignKey(Cidade, on_delete=models.CASCADE)

    def __str__(self):
        return self.nome

class Cliente(CustomUser):
    is_active = models.BooleanField(_('active'), default=False)
    estado = models.ForeignKey(Estado, on_delete=models.CASCADE, blank=True, null=True)
    cidade = models.ForeignKey(Cidade, on_delete=models.CASCADE, blank=True, null=True)
    bairro = models.ForeignKey(Bairro, on_delete=models.CASCADE, blank=True, null=True)

class Profissional(CustomUser):
    is_active = models.BooleanField(_('active'), default=False)
    estado = models.ForeignKey(Estado, on_delete=models.CASCADE, blank=True, null=True)
    cidade = models.ForeignKey(Cidade, on_delete=models.CASCADE, blank=True, null=True)
    bairro = models.ForeignKey(Bairro, on_delete=models.CASCADE, blank=True, null=True)
    convenio = models.ManyToManyField('Convenio')
    tipo_profissional = models.CharField(max_length=50, choices=TIPO_PROFISSIONAL_CHOICES, blank=True)
    servicos = models.ManyToManyField('Servico')
    idiomas = models.ManyToManyField('Idioma')
    especialidades = models.ManyToManyField('Especialidade')
    
    codigo = models.CharField( max_length=30, blank=True)

class Clinica(AbstractBaseUser, PermissionsMixin):
    is_active = models.BooleanField(_('active'), default=False)
    estado = models.ForeignKey(Estado, on_delete=models.CASCADE, blank=True, null=True)
    cidade = models.ForeignKey(Cidade, on_delete=models.CASCADE, blank=True, null=True)
    bairro = models.ForeignKey(Bairro, on_delete=models.CASCADE, blank=True, null=True)
    convenio = models.ManyToManyField('Convenio')
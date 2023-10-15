from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.contrib.contenttypes.fields import GenericRelation

from django.utils import timezone
from django.utils.translation import gettext_lazy as _
import uuid
from django import forms
from PIL import Image
import requests
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


TIPO_PROFISSIONAL_CHOICES = [
    ('Médico', 'Médico'),
    ('Dentista', 'Dentista'),
    # ... adicione outros tipos conforme necessário
]



ESPECIALIDADE_CHOICES = [
    ('Cardiologista', 'Cardiologista'),
    ('Ortopedista', 'Ortopedista'),
    # Adicione mais aqui
]

CONVENIO_CHOICES = [
    ('Médico', 'Médico'),
    ('Dentista', 'Dentista'),
    ('Ambos', 'Ambos'),
    # ... adicione outros tipos conforme necessário
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
    tipo_profissional = models.CharField(max_length=50, choices=CONVENIO_CHOICES, blank=True)
    

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


class TipoClinica(models.Model):
    nome = models.CharField(max_length=100)
   
    def __str__(self):
        return self.nome

class TipoProfissional(models.Model):
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


class CEP(models.Model):
    codigo = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return self.codigo

class Avaliacao(models.Model):
    RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]
    rating = models.IntegerField(choices=RATING_CHOICES)
    descricao = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # Vinculando com o Cliente que fez a avaliação
    cliente = models.ForeignKey('Cliente', related_name='avaliacoes', on_delete=models.CASCADE)

    # Campos para relacionamento genérico
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

class PerguntaResposta(models.Model):
    pergunta = models.TextField()
    resposta = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Campos para relacionamento genérico
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')    

class Endereco(models.Model):
    rua = models.CharField(max_length=255)
    numero = models.IntegerField(null=True, blank=True)
    complemento = models.CharField(max_length=50, null=True, blank=True)
    bairro = models.ForeignKey(Bairro, on_delete=models.CASCADE)
    cidade = models.ForeignKey(Cidade, on_delete=models.CASCADE)
    estado = models.ForeignKey(Estado, on_delete=models.CASCADE)
    cep = models.ForeignKey(CEP, on_delete=models.CASCADE)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    profissional = models.ForeignKey('Profissional', related_name='enderecos_fk', on_delete=models.CASCADE, null=True, blank=True)
    clinica = models.ForeignKey('Clinica', related_name='enderecos_fk', on_delete=models.CASCADE, null=True, blank=True)
    
    def __str__(self):
        return f"{self.rua}, {self.bairro}, {self.cidade}, {self.estado}, {self.cep}, {self.complemento}, {self.latitude}, {self.longitude}"

from django.db.models import Avg


class Cliente(CustomUser):
    is_active = models.BooleanField(_('active'), default=False)
    estado = models.ForeignKey(Estado, on_delete=models.CASCADE, blank=True, null=True)
    cidade = models.ForeignKey(Cidade, on_delete=models.CASCADE, blank=True, null=True)
    bairro = models.ForeignKey(Bairro, on_delete=models.CASCADE, blank=True, null=True)
    foto = models.ImageField(upload_to='images/', blank=True, null=True, default="/images/unknown.png")
    cep = models.CharField(max_length=50, blank=True, null=True)

class Profissional(CustomUser):
    is_active = models.BooleanField(_('active'), default=False)
    estado = models.ManyToManyField('Estado', blank=True)
    cidade = models.ManyToManyField('Cidade', blank=True)
    bairro = models.ManyToManyField('Bairro', blank=True)
    convenios = models.ManyToManyField('Convenio', blank=True)
    tipo_profissional = models.CharField(max_length=50, choices=TIPO_PROFISSIONAL_CHOICES, blank=True)
    servicos = models.ManyToManyField('Servico', blank=True)
    idiomas = models.ManyToManyField('Idioma', blank=True)
    especialidades = models.ManyToManyField('Especialidade')
    foto = models.ImageField(upload_to='images/', blank=True, null=True, default="/images/unknown.png")
    codigo = models.CharField( max_length=30, blank=True)
    enderecos = models.ManyToManyField(Endereco, blank=True, related_name='profissionais')
    ceps = models.ManyToManyField(CEP, blank=True, related_name='profissionais')
    descricao = models. TextField(blank=True)
    avaliacoes = GenericRelation(Avaliacao)
    perguntas_respostas = GenericRelation(PerguntaResposta)
    
    def save(self, *args, **kwargs):
        if not self.foto:
            if self.tipo_profissional == "Médico":
                self.foto = "/images/medico_default.png"
            elif self.tipo_profissional == "Dentista":
                self.foto = "/images/dentista_default.png"
            # adicione mais condições conforme necessário
            else:
                self.foto = "/images/unknown.png"
        super(Profissional, self).save(*args, **kwargs)

class Clinica(CustomUser):
   
    is_active = models.BooleanField(_('active'), default=False)
    estados = models.ManyToManyField('Estado', blank=True)
    cidades = models.ManyToManyField('Cidade', blank=True)
    bairros = models.ManyToManyField('Bairro', blank=True)
    convenios = models.ManyToManyField('Convenio', blank=True)
    tipo_clinica = models.ManyToManyField('TipoClinica', blank=True)
    tipo_profissional = models.ManyToManyField('TipoProfissional', blank=True)
    especialidades = models.ManyToManyField('Especialidade')
    servicos = models.ManyToManyField('Servico', blank=True)
    idiomas = models.ManyToManyField('Idioma', blank=True)
    foto = models.ImageField(upload_to='images/', blank=True, null=True, default="/images/unknown.png")
    ceps = models.ManyToManyField(CEP, blank=True, related_name='clinicas')
    enderecos = models.ManyToManyField(Endereco, blank=True, related_name='clinicas')
    descricao = models. TextField(blank=True)
    avaliacoes = GenericRelation(Avaliacao)
    perguntas_respostas = GenericRelation(PerguntaResposta)
    
    def save(self, *args, **kwargs):
        if not self.foto:
            if "Emergência" in self.tipo_clinica.values_list('nome', flat=True):
                self.foto = "/images/hospital_default.png"
            elif "Laboratório" in self.tipo_clinica.values_list('nome', flat=True):
                self.foto = "/images/laboratorio_dental_default.png"
            # adicione mais condições conforme necessário
            else:
                self.foto = "/images/unknown.png"
        super(Clinica, self).save(*args, **kwargs)








def get_lat_lng_from_cep(cep):
    response = requests.get(f'https://viacep.com.br/ws/{cep}/json/')
    data = response.json()
    localidade = data.get('localidade')
    uf = data.get('uf')

    response = requests.get(f'https://nominatim.openstreetmap.org/search?city={localidade}&state={uf}&format=json')
    data = response.json()
    if data:
        latitude = float(data[0]['lat'])
        longitude = float(data[0]['lon'])
        return latitude, longitude
    else:
        return None, None
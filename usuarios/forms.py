from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm
from .models import Profissional, Cliente
from .models import *


class ProfissionalRegistrationForm(UserCreationForm):
    
    especialidades = forms.ModelMultipleChoiceField(
        queryset=Especialidade.objects.all(), 
        widget=forms.CheckboxSelectMultiple, 
        required=False)
    convenio = forms.ModelMultipleChoiceField(
        queryset=Convenio.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    
   
    image = forms.ImageField(required=False)
    
    
    
  
    class Meta:
        model = Profissional
        fields = ['email', 'password1', 'password2', 
                  'tipo_profissional', 'ceps', 'especialidades', 
                  'telefone', 'nome', 'sobrenome', 'username', 'foto', 'codigo', 'convenios', 'descricao',  'idiomas']

    def __init__(self, *args, **kwargs):
        super(ProfissionalRegistrationForm, self).__init__(*args, **kwargs)
        self.fields['especialidades'].choices = [(x.id, x.nome) for x in Especialidade.objects.all()]

        
        
class ClienteRegistrationForm(UserCreationForm):
    cep = forms.CharField(max_length=9, required=True)
    image = forms.ImageField(required=False)
    

    class Meta:
        model = Cliente
        fields = ['email', 'password1', 'password2', 'cep', 'nome', 'sobrenome', 'username', 'telefone', 'foto']
        
        
        
class ClinicaForm(UserCreationForm):
    
    image = forms.ImageField(required=False)
    
    tipo_clinica = forms.ModelMultipleChoiceField(
        queryset=TipoClinica.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    
    tipo_profissional = forms.ModelMultipleChoiceField(
        queryset=TipoProfissional.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    
    
    especialidades = forms.ModelMultipleChoiceField(
        queryset=Especialidade.objects.all(), 
        widget=forms.CheckboxSelectMultiple, 
        required=False)
    
    estados = forms.ModelMultipleChoiceField(
        queryset=Estado.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    
    cidades = forms.ModelMultipleChoiceField(
        queryset=Cidade.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    
    bairros = forms.ModelMultipleChoiceField(
        queryset=Bairro.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    
    convenio = forms.ModelMultipleChoiceField(
        queryset=Convenio.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    
    class Meta:
        model = Clinica
        fields = ['email', 'password1', 'password2', 'especialidades', 
                  'telefone', 'nome', 'sobrenome', 'username', 'image', 'convenios', 'idiomas','tipo_clinica', 'descricao', 'tipo_profissional', 'foto']
        

from django.forms import inlineformset_factory
from .models import Profissional, Foto
class FotoForm(forms.ModelForm):
    class Meta:
        model = Foto
        fields = ['imagem', 'descricao']


FotoFormSet = inlineformset_factory(Profissional, Foto, form=FotoForm, extra=1, fields=['imagem', 'descricao'])

class ProfissionalUpdateForm(forms.ModelForm):
    class Meta:
        model = Profissional
        fields = ['foto', 'descricao', 'convenios', 'servicos', 'idiomas']  # os campos foto, descricao e convenios apenas


class ClinicaUpdateForm(forms.ModelForm):
    class Meta:
        model = Profissional
        fields = ['foto', 'descricao', 'convenios', 'servicos', 'idiomas']  # os campos foto, descricao e convenios apenas
        
        
                
FotoFormSetClinica = inlineformset_factory(Clinica, Foto, form=FotoForm, extra=1, fields=['imagem', 'descricao'])

class ClinicaUpdateForm(forms.ModelForm):
    class Meta:
        model = Clinica
        fields = ['foto', 'descricao', 'convenios', 'servicos', 'idiomas']  # os campos foto, descricao e convenios apenas        

# forms.py
from django import forms
from .models import Endereco

class EnderecoForm(forms.ModelForm):
    class Meta:
        model = Endereco
        fields = ['latitude', 'longitude']


class LoginForm(AuthenticationForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class':'form-control', 'placeholder': 'Email'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control', 'placeholder':'Senha'}))
    

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        self.fields['username'] = self.fields.get('email')
        
        
class AvaliacaoForm(forms.ModelForm):
    class Meta:
        model = Avaliacao
        fields = ['rating', 'descricao']
        
class ProfissionalForm(forms.ModelForm):
    class Meta:
        model = Profissional
        fields = ['nome', 'sobrenome', 'descricao', 'telefone', 'convenios', 'idiomas', 'servicos', 'galeria']


class ClinicaForm(forms.ModelForm):
    class Meta:
        model = Profissional
        fields = ['nome', 'sobrenome', 'descricao', 'telefone', 'convenios', 'idiomas', 'servicos', 'galeria']
                
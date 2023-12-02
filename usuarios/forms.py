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
                  'telefone', 'nome', 'sobrenome', 'username', 'foto', 'codigo', 'convenios', 'descricao',  'idiomas', 'diploma']

    def __init__(self, *args, **kwargs):
        super(ProfissionalRegistrationForm, self).__init__(*args, **kwargs)
        self.fields['especialidades'].choices = [(x.id, x.nome) for x in Especialidade.objects.all()]
        
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if Profissional.objects.filter(username=username).exists():
            raise forms.ValidationError('Este nome de usuário já foi tomado.')
        return username
        
class ClinicaForm(UserCreationForm):
    
    image = forms.ImageField(required=False)
    
    class Meta:
        model = Clinica
        fields =  ['email', 'password1', 'password2', 
                  'tipo_profissional', 'ceps', 'especialidades', 
                  'telefone', 'nome',  'username', 'foto', 'convenios', 'descricao',  'idiomas', 'tipo_clinica']        

class AddressUpdateForm(forms.Form):
    # Seus campos de endereço vêm aqui. Como você está lidando com múltiplos
    # endereços e os dados são processados manualmente em sua view,
    # você pode não precisar de campos específicos aqui.
    pass  # Placeholder, remova esta linha quando adicionar campos        
        
class ClienteRegistrationForm(UserCreationForm):
    cep = forms.CharField(max_length=9, required=True)
    image = forms.ImageField(required=False)
    

    class Meta:
        model = Cliente
        fields = ['email', 'password1', 'password2', 'cep', 'nome', 'sobrenome', 'username', 'telefone', 'foto']
        
        
        

        

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
    username = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control', 'placeholder': 'Email ou CPF'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control', 'placeholder':'Senha'}))
        
        
class AvaliacaoForm(forms.ModelForm):
    class Meta:
        model = Avaliacao
        fields = ['rating', 'descricao']
        
class PerguntaRespostaForm(forms.ModelForm):
    class Meta:
        model = PerguntaResposta
        fields = ['pergunta']  # Você pode adicionar mais campos se necessário
    
    # Caso você queira adicionar alguma validação específica ou outros métodos
    def clean_pergunta(self):
        pergunta = self.cleaned_data.get('pergunta')
        if not pergunta:
            raise forms.ValidationError("Este campo não pode ser deixado em branco.")
        return pergunta


class RespostaForm(forms.ModelForm):
    class Meta:
        model = PerguntaResposta  # supondo que 'Pergunta' é o seu modelo que possui o campo 'resposta'
        fields = ['resposta']
    
    
class ProfissionalForm(forms.ModelForm):
    def clean_galeria(self):
        data = self.cleaned_data.get('galeria', None)
        if data is None or data == '':
            return None  # Ou qualquer valor padrão
        return data

    class Meta:
        model = Profissional
        fields = ['nome', 'sobrenome', 'descricao', 'telefone', 'convenios', 'idiomas', 'servicos', 'galeria', 'preco']
        
        
class ClinicaEditarForm(forms.ModelForm):
    def clean_galeria(self):
        data = self.cleaned_data.get('galeria', None)
        if data is None or data == '':
            return None  # Ou qualquer valor padrão
        return data

    class Meta:
        model = Clinica
        fields = ['nome', 'descricao', 'telefone', 'convenios', 'idiomas', 'servicos', 'galeria']
        
        
class FotoProfForm(forms.ModelForm):

    class Meta:
        model = Profissional
        fields = ['foto']        


class FotoClinicaForm(forms.ModelForm):

    class Meta:
        model = Clinica
        fields = ['foto']        


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



from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth import get_user_model

User = get_user_model()

class EmailPasswordResetForm(PasswordResetForm):
    def get_users(self, email):
        """ Retorna um conjunto de usuários correspondentes para redefinição de senha. """
        # Busca usuários pelo e-mail, independente do estado 'is_active'
        active_users = User._default_manager.filter(email__iexact=email)
        return (u for u in active_users if u.has_usable_password())



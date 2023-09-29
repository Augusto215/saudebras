from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm
from .models import Profissional, Cliente
from .models import CustomUser, Especialidade


class ProfissionalRegistrationForm(UserCreationForm):
    cep = forms.CharField(max_length=9, required=True)
    especialidades = forms.ModelMultipleChoiceField(
        queryset=Especialidade.objects.all(), 
        widget=forms.CheckboxSelectMultiple, 
        required=False
    )
    
    
    telefone = forms.CharField(max_length=20, required=False)
    nome = forms.CharField(max_length=100, required=True)
    sobrenome = forms.CharField(max_length=100, required=True)
    cpf = forms.CharField(max_length=14, required=False)

    class Meta:
        model = Profissional
        fields = ['email', 'password1', 'password2', 
                  'tipo_profissional', 'cep', 'especialidades', 
                  'telefone', 'nome', 'sobrenome', 'username']

    def __init__(self, *args, **kwargs):
        super(ProfissionalRegistrationForm, self).__init__(*args, **kwargs)
        self.fields['especialidades'].choices = [(x.id, x.nome) for x in Especialidade.objects.all()]

        
        
class ClienteRegistrationForm(UserCreationForm):
    cep = forms.CharField(max_length=9, required=True)
    

    class Meta:
        model = Cliente
        fields = ['email', 'password1', 'password2', 'cep', 'nome', 'sobrenome', 'username', 'telefone']

class LoginForm(AuthenticationForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class':'form-control', 'placeholder': 'Email'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control', 'placeholder':'Senha'}))
    

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        self.fields['username'] = self.fields.get('email')
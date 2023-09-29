from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.core.mail import send_mail
from django.http import JsonResponse
from .forms import ClienteRegistrationForm, ProfissionalRegistrationForm, LoginForm
import uuid
from .models import *
from datetime import timedelta
from django.utils import timezone
from .models import Bairro, Cidade, Estado # Adicionei as importações dos modelos Dentista e Medico
import requests
from django.contrib import messages



from django.shortcuts import render, redirect
from .forms import ClienteRegistrationForm, ProfissionalRegistrationForm
from .models import Cliente, Profissional, Estado, Cidade, Bairro

def registerProfissional(request):
    form = ProfissionalRegistrationForm()

    if request.method == 'POST':
        form = ProfissionalRegistrationForm(request.POST)

        if form.is_valid():
            # Processando o CEP
            cep = form.cleaned_data['cep']
            response = requests.get(f'https://viacep.com.br/ws/{cep}/json/')
            data = response.json()

            if response.status_code == 200 and not data.get('erro'):
                estado, _ = Estado.objects.get_or_create(nome=data['uf'])
                cidade, _ = Cidade.objects.get_or_create(nome=data['localidade'], estado=estado)
                bairro, _ = Bairro.objects.get_or_create(nome=data['bairro'], cidade=cidade)

                user = Profissional.objects.create_user(
                    nome=form.cleaned_data['nome'],
                    sobrenome=form.cleaned_data['sobrenome'],
                    username=form.cleaned_data['username'],
                    telefone=form.cleaned_data['telefone'],
                    email=form.cleaned_data['email'],
                    password=form.cleaned_data['password1'],
                    estado=estado,
                    cidade=cidade,
                    bairro=bairro,
                    tipo_profissional=form.cleaned_data['tipo_profissional'],
                )

                # Configurando as especialidades
                selected_especialidades = form.cleaned_data['especialidades']
                user.especialidades.set(selected_especialidades)
                user.save()

                return redirect('login')
            else:
                print("CEP inválido ou não encontrado")
        else:
            print("Formulário inválido")
            print(form.errors)

    return render(request, 'core/index.html', {'form': form})


def registerCliente(request):
    form = ClienteRegistrationForm()

    if request.method == 'POST':
        form = ClienteRegistrationForm(request.POST)
        
        if form.is_valid():
            # Processa o CEP
            cep = form.cleaned_data['cep']
            response = requests.get(f'https://viacep.com.br/ws/{cep}/json/')
            data = response.json()
            
            if response.status_code == 200 and not data.get('erro'):
                estado, _ = Estado.objects.get_or_create(nome=data['uf'])
                cidade, _ = Cidade.objects.get_or_create(nome=data['localidade'], estado=estado)
                bairro, _ = Bairro.objects.get_or_create(nome=data['bairro'], cidade=cidade)

                user = Cliente.objects.create_user(
                    nome = form.cleaned_data['nome'],
                    sobrenome = form.cleaned_data['sobrenome'],
                    username = form.cleaned_data['username'],
                    telefone = form.cleaned_data['telefone'],
                    email=form.cleaned_data['email'],
                    password=form.cleaned_data['password1'],
                    estado=estado,
                    cidade=cidade,
                    bairro=bairro,
                 
                  
                )
                user.save()

             
               
               
                    
                return redirect('login')
            else:
                print("CEP inválido ou não encontrado")
        else:
            print("Formulário inválido")
            print(form.errors)
    
    return render(request, 'core/', {'form': form})


from django.contrib.auth import login as auth_login
from .forms import LoginForm
from django.contrib.auth import authenticate

def user_login(request):
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        email = request.POST['username']
        password = request.POST['password']
        user = authenticate(email=email, password=password)
        
        if user is not None:
            auth_login(request, user)
            messages.success(request, "Login successfully!")
            return redirect('home')
        else:
            messages.error(request, "Invalid email or password.")
    else:
        form = LoginForm()
        
    return render(request, 'core/index.html', {'form': form})
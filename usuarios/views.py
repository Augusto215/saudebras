from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.core.serializers import serialize

from django.core.mail import send_mail
from django.http import JsonResponse
from django.db import transaction
import requests
from geopy.geocoders import Nominatim
import time
from usuarios.forms import *
from django.core.exceptions import ObjectDoesNotExist

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404



from .forms import *
import uuid
from .models import *
from datetime import timedelta
from django.utils import timezone
from .models import Bairro, Cidade, Estado # Adicionei as importações dos modelos Dentista e Medico
import requests
from django.contrib import messages
from usuarios.models import Especialidade

from django.forms import formset_factory


from django.shortcuts import render, redirect
from .forms import ClienteRegistrationForm, ProfissionalRegistrationForm
from .models import Cliente, Profissional, Estado, Cidade, Bairro





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
                    foto = form.cleaned_data['foto'],
                    password=form.cleaned_data['password1'],
                    estado=estado,
                    cidade=cidade,
                    bairro=bairro,
                    cep=cep,
                 
                  
                )
                user.save()

             
               
               
                    
                return redirect('login')
            else:
                print("CEP inválido ou não encontrado")
        else:
            print("Formulário inválido")
            print(form.errors)
    
    return render(request, 'core/registroClientes.html', {'form': form})






from django.shortcuts import render, redirect
from .models import Clinica, Estado, Cidade, Bairro, TipoClinica, Especialidade, Convenio, Idioma
from .forms import ClinicaForm
import requests

from django.db import transaction
import requests
from .models import Especialidade, TipoClinica, TipoProfissional, Idioma, Convenio, Estado, Cidade, Bairro, CEP, Endereco
from django.shortcuts import render, redirect
from .forms import ClinicaForm

import googlemaps

def obter_coordenadas(endereco_completo, google_maps_api_key):
    gmaps = googlemaps.Client(key=google_maps_api_key)
    geocode_result = gmaps.geocode(endereco_completo)
    
    if geocode_result:
        latitude = geocode_result[0]['geometry']['location']['lat']
        longitude = geocode_result[0]['geometry']['location']['lng']
        return latitude, longitude
    
    return None, None



def registerProfissional(request):
    especialidades = Especialidade.objects.all()
    idiomas = Idioma.objects.all()
    convenios = Convenio.objects.all()
    tipo_profissional = TipoProfissional.objects.all()
    form = ProfissionalRegistrationForm()

    if request.method == 'POST':
        form = ProfissionalRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            with transaction.atomic():  # Início da transação atômica
                user = form.save(commit=False)

                enderecos = []
                estados = []
                cidades = []
                bairros = []
                ceps_list = []
                
                user.save()
                ceps = request.POST.getlist('cep[]')
                complementos = request.POST.getlist('complemento[]')
                for i, cep in enumerate(ceps):
                    response = requests.get(f'https://viacep.com.br/ws/{cep}/json/')
                    data = response.json()
                    
                    if response.status_code == 200 and not data.get('erro'):
                        estado, _ = Estado.objects.get_or_create(nome=data['uf'])
                        cidade, _ = Cidade.objects.get_or_create(nome=data['localidade'], estado=estado)
                        bairro, _ = Bairro.objects.get_or_create(nome=data['bairro'], cidade=cidade)
                        cep_obj, _ = CEP.objects.get_or_create(codigo=cep)
                        endereco_completo = f"{data['logradouro']}, {data['bairro']}, {data['localidade']}, {data['uf']}, {data['cep']}"
                        latitude, longitude = obter_coordenadas(endereco_completo, "AIzaSyBLZ8D6WJwaCql2h4-UGjibK4tx9MhZmXE")
                        
                        
                        complemento_atual = complementos[i]
                        endereco, _ = Endereco.objects.get_or_create(
                            rua=data['logradouro'],
                            complemento=complemento_atual,
                            bairro=bairro,
                            cidade=cidade,
                            estado=estado,
                            cep=cep_obj,
                            latitude=latitude,  # Adicionado
                            longitude=longitude,
                            profissional=user
                            
                        )

                        estados.append(estado)
                        cidades.append(cidade)
                        bairros.append(bairro)
                        enderecos.append(endereco)
                        ceps_list.append(cep_obj)

                # Salve o usuário antes de adicionar relações
                user.save()
                    
                user.set_password(form.cleaned_data['password1'])
                user.tipo_profissional = form.cleaned_data['tipo_profissional']
                user.email =form.cleaned_data['email']
                user.telefone = form.cleaned_data['telefone']
                user.nome = form.cleaned_data['nome']
                user.username = form.cleaned_data['username']
                user.sobrenome = form.cleaned_data['sobrenome']
                user.descricao = form.cleaned_data['descricao']
                user.codigo = form.cleaned_data['codigo']
                user.foto = form.cleaned_data['foto']
                selected_especialidades = form.cleaned_data['especialidades']
                selected_convenios = form.cleaned_data['convenios']
                selected_idiomas = form.cleaned_data['idiomas']
                
                user.estado.set(estados)
                user.cidade.set(cidades)
                user.bairro.set(bairros)
                user.ceps.set(ceps_list)
                user.especialidades.set(selected_especialidades)
                user.convenios.set(selected_convenios)
                user.idiomas.set(selected_idiomas)
                user.enderecos.set(enderecos)

                user.save()

                return redirect('login')

        else:
            print("Formulário inválido")
            print(form.errors)

    context = {
        'especialidades': especialidades,
        'convenios': convenios,
        'idiomas': idiomas,
        'form': form,
        'tipo_profissionais': tipo_profissional,
    }

    return render(request, 'core/registroProfissionais.html', context)

    



def registerClinica(request):
    especialidades = Especialidade.objects.all()
    tipo_clinica = TipoClinica.objects.all()
    tipo_profissional = TipoProfissional.objects.all()
    idiomas = Idioma.objects.all()
    convenios = Convenio.objects.all()
    form = ClinicaForm()

    if request.method == 'POST':
        form = ClinicaForm(request.POST, request.FILES)
        if form.is_valid():
            with transaction.atomic():  # Início da transação atômica
                clinica = form.save(commit=False)

                enderecos = []
                estados = []
                cidades = []
                bairros = []
                ceps_list = []

                
                clinica.save()
                ceps = request.POST.getlist('cep[]')
                complementos = request.POST.getlist('complemento[]')
                for i, cep in enumerate(ceps):
                    response = requests.get(f'https://viacep.com.br/ws/{cep}/json/')
                    data = response.json()
                    
                    if response.status_code == 200 and not data.get('erro'):
                        estado, _ = Estado.objects.get_or_create(nome=data['uf'])
                        cidade, _ = Cidade.objects.get_or_create(nome=data['localidade'], estado=estado)
                        bairro, _ = Bairro.objects.get_or_create(nome=data['bairro'], cidade=cidade)
                        cep_obj, _ = CEP.objects.get_or_create(codigo=cep)
                        endereco_completo = f"{data['logradouro']}, {data['bairro']}, {data['localidade']}, {data['uf']}, {data['cep']}"
                        latitude, longitude = obter_coordenadas(endereco_completo, "AIzaSyBLZ8D6WJwaCql2h4-UGjibK4tx9MhZmXE")
                        complemento_atual = complementos[i]
                        endereco, _ = Endereco.objects.get_or_create(

                                rua=data['logradouro'],
                                complemento=complemento_atual,
                                bairro=bairro,
                                cidade=cidade,
                                estado=estado,
                                cep=cep_obj,
                                latitude=latitude,  # Adicionado
                                longitude=longitude,
                                clinica=clinica
                            )

                        estados.append(estado)
                        cidades.append(cidade)
                        bairros.append(bairro)
                        enderecos.append(endereco)
                        ceps_list.append(cep_obj)

                # Agora, salve a clínica antes de adicionar relações
                clinica.save()
                    
                clinica.set_password(form.cleaned_data['password1'])
                clinica.email = form.cleaned_data['email']
                clinica.telefone = form.cleaned_data['telefone']
                clinica.nome = form.cleaned_data['nome']
                clinica.sobrenome = form.cleaned_data['sobrenome']
                clinica.username = form.cleaned_data['username']
                clinica.descricao = form.cleaned_data['descricao']
                clinica.foto = form.cleaned_data['foto']
                selected_tipoClinica = form.cleaned_data['tipo_clinica']
                selected_tipoProfissional = form.cleaned_data['tipo_profissional']
                selected_especialidades = form.cleaned_data['especialidades']
                selected_convenios = form.cleaned_data['convenios']
                selected_idiomas = form.cleaned_data['idiomas']
                
                

                clinica.estados.set(estados)
                clinica.tipo_clinica.set(selected_tipoClinica)
                clinica.cidades.set(cidades)
                clinica.bairros.set(bairros)
                clinica.ceps.set(ceps_list)
                clinica.tipo_profissional.set(selected_tipoProfissional)
                clinica.convenios.set(selected_convenios)
                clinica.especialidades.set(selected_especialidades)
                clinica.idiomas.set(selected_idiomas)
                clinica.enderecos.set(enderecos)
                

                clinica.save()

                return redirect('login')

        
            
        else:
            print("Formulário inválido")
            print(form.errors)

    context = {
        'especialidades': especialidades,
        'convenios': convenios,
        'idiomas': idiomas,
        'form': form,
        'tipos_clinicas': tipo_clinica,
        'tipos_profissionais': tipo_profissional
    }

    return render(request, 'core/registroClinicas.html', context)






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
        
    return render(request, 'core/login.html', {'form': form})

def convenios_perfil(request):
    profissional = request.user.profissional
    convenios = Convenio.objects.all()

    # Serializar os objetos em JSON
    convenios_json = serialize('json', convenios)
    prof_convenios_json = serialize('json', profissional.convenios.all())

    return JsonResponse({'convenios': convenios_json, 'prof_convenios': prof_convenios_json})

#EDITAR PERFIL
@login_required
def editar_perfil(request):
    profissional = request.user.profissional
    convenios = Convenio.objects.all()
    idiomas = Idioma.objects.all()
    servicos = Servico.objects.all()
    fotos = Foto.objects.all()
    
    if request.method == 'POST':
        acao = request.POST.get('acao')
        profissional_form = ProfissionalUpdateForm(request.POST, instance=request.user.profissional)
        endereco_form = EnderecoForm(request.POST)
        
        if profissional_form.is_valid():
            profissional_form.save()
        
        if acao == 'criar':
            if endereco_form.is_valid():
                novo_endereco = endereco_form.save(commit=False)
                novo_endereco.profissional = request.user.profissional
                novo_endereco.save()
                messages.success(request, 'Endereço adicionado com sucesso.')
        elif acao == 'editar':
            endereco_id = request.POST.get('endereco_id')
            try:
                endereco_instance = Endereco.objects.get(id=endereco_id, profissional=request.user.profissional)
                endereco_form = EnderecoForm(instance=endereco_instance)
            except Endereco.DoesNotExist:
                messages.error(request, 'Endereço não encontrado.')

        elif acao == 'atualizar':
            endereco_id = request.POST.get('endereco_id')
            try:
                endereco_instance = Endereco.objects.get(id=endereco_id, profissional=request.user.profissional)
                endereco_form = EnderecoForm(request.POST, instance=endereco_instance)
                if endereco_form.is_valid():
                    endereco_form.save()
                    messages.success(request, 'Endereço atualizado com sucesso.')
            except Endereco.DoesNotExist:
                messages.error(request, 'Endereço não encontrado.')
        
        elif acao == 'excluir':
            endereco_id = request.POST.get('endereco_id')
            try:
                endereco = Endereco.objects.get(id=endereco_id, profissional=request.user.profissional)
                endereco.delete()
                messages.success(request, 'Endereço excluído com sucesso.')
            except Endereco.DoesNotExist:
                messages.error(request, 'Endereço não encontrado.')
    else:
        profissional_form = ProfissionalUpdateForm(instance=request.user.profissional)
        endereco_form = EnderecoForm()

    enderecos_do_profissional = Endereco.objects.filter(profissional=request.user.profissional)
    return render(request, 'core/editar_profissional.html', {
        'profissional_form': profissional_form,
        'endereco_form': endereco_form,
        'enderecos': enderecos_do_profissional,
        'convenios':convenios,
        'idiomas':idiomas,
        'servicos':servicos,
        'profissional':profissional,
        'fotos':fotos
    })

from django.contrib import messages

def alterar_Profissional(request):
    user = request.user.profissional
    if request.method == 'POST':
        form = ProfissionalForm(request.POST, request.FILES, instance=user)
        print(f"Data Received: {request.POST}")  # Debug: mostrar dados recebidos
        if form.is_valid():
            cleaned_data = form.cleaned_data
            print(f"Cleaned Data: {cleaned_data}")  # Debug: mostrar dados limpos

            # Atualiza campos comuns
            user.nome = form.cleaned_data['nome']
            user.sobrenome = cleaned_data.get('sobrenome', '')
            user.descricao = cleaned_data.get('descricao', '')
            user.telefone = cleaned_data.get('telefone', '')
            print(f"User Before Save: {vars(user)}")  # Debug: mostrar estado do user antes de salvar
            
            # Salva as mudanças para que a instância esteja atualizada
            user.save()
            
            # Atualiza os campos ManyToMany
            user.convenios.set(cleaned_data.get('convenios', []))
            user.idiomas.set(cleaned_data.get('idiomas', []))
            user.servicos.set(cleaned_data.get('servicos', []))
            user.galeria.set(cleaned_data.get('galeria', []))

            user.save()

            messages.success(request, 'Perfil atualizado com sucesso!')
            return redirect('editar_perfil')
        else:
            print(f"Form Errors: {form.errors}")  # Debug: mostrar erros de validação
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Erro no campo {field}: {error}")
    else:
        # Logica para o GET caso necessário
        pass

    return render(request, 'core/editar_profissional.html')



    
#EDITAR PERFIL
@login_required
def editar_perfil_clinica(request):
    clinica = request.user.clinica
    convenios = Convenio.objects.all()
    idiomas = Idioma.objects.all()
    servicos = Servico.objects.all()
    fotos = Foto.objects.all()
    
    if request.method == 'POST':
        acao = request.POST.get('acao')
        clinica_form = ClinicaUpdateForm(request.POST, instance=request.user.clinica)
        endereco_form = EnderecoForm(request.POST)
        
        if profissional_form.is_valid():
            profissional_form.save()
        
        if acao == 'criar':
            if endereco_form.is_valid():
                novo_endereco = endereco_form.save(commit=False)
                novo_endereco.clinica = request.user.clinica
                novo_endereco.save()
                messages.success(request, 'Endereço adicionado com sucesso.')
        elif acao == 'editar':
            endereco_id = request.POST.get('endereco_id')
            try:
                endereco_instance = Endereco.objects.get(id=endereco_id, clinica=request.user.clinica)
                endereco_form = EnderecoForm(instance=endereco_instance)
            except Endereco.DoesNotExist:
                messages.error(request, 'Endereço não encontrado.')

        elif acao == 'atualizar':
            endereco_id = request.POST.get('endereco_id')
            try:
                endereco_instance = Endereco.objects.get(id=endereco_id, profissional=request.user.clinica)
                endereco_form = EnderecoForm(request.POST, instance=endereco_instance)
                if endereco_form.is_valid():
                    endereco_form.save()
                    messages.success(request, 'Endereço atualizado com sucesso.')
            except Endereco.DoesNotExist:
                messages.error(request, 'Endereço não encontrado.')
        
        elif acao == 'excluir':
            endereco_id = request.POST.get('endereco_id')
            try:
                endereco = Endereco.objects.get(id=endereco_id, profissional=request.user.clinica)
                endereco.delete()
                messages.success(request, 'Endereço excluído com sucesso.')
            except Endereco.DoesNotExist:
                messages.error(request, 'Endereço não encontrado.')
    else:
        profissional_form = ClinicaUpdateForm(instance=request.user.clinica)
        endereco_form = EnderecoForm()

    enderecos_do_profissional = Endereco.objects.filter(clinica=request.user.clinica)
    return render(request, 'core/editar_clinica.html', {
        'profissional_form': profissional_form,
        'endereco_form': endereco_form,
        'enderecos': enderecos_do_profissional,
        'convenios':convenios,
        'idiomas':idiomas,
        'servicos':servicos,
        'clinica':clinica,
        'fotos':fotos
    })
        
        

def alterar_Clinica(request):
    user = request.user.clinica
    if request.method == 'POST':
        form = ClinicaForm(request.POST, request.FILES, instance=user)
        print(f"Data Received: {request.POST}")  # Debug: mostrar dados recebidos
        if form.is_valid():
            cleaned_data = form.cleaned_data
            print(f"Cleaned Data: {cleaned_data}")  # Debug: mostrar dados limpos

            # Atualiza campos comuns
            user.nome = form.cleaned_data['nome']
            user.sobrenome = cleaned_data.get('sobrenome', '')
            user.descricao = cleaned_data.get('descricao', '')
            user.telefone = cleaned_data.get('telefone', '')
            print(f"User Before Save: {vars(user)}")  # Debug: mostrar estado do user antes de salvar
            
            # Salva as mudanças para que a instância esteja atualizada
            user.save()
            
            # Atualiza os campos ManyToMany
            user.convenios.set(cleaned_data.get('convenios', []))
            user.idiomas.set(cleaned_data.get('idiomas', []))
            user.servicos.set(cleaned_data.get('servicos', []))
            user.galeria.set(cleaned_data.get('galeria', []))

            user.save()

            messages.success(request, 'Perfil atualizado com sucesso!')
            return redirect('editar_perfil')
        else:
            print(f"Form Errors: {form.errors}")  # Debug: mostrar erros de validação
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Erro no campo {field}: {error}")
    else:
        # Logica para o GET caso necessário
        pass

    return render(request, 'core/editar_clinica.html')

    
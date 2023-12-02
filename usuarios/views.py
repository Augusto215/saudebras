from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.core.serializers import serialize
from django.core.files.storage import default_storage
from django.db.models import Q
from django.db import IntegrityError, transaction
from django.db import OperationalError
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.http import JsonResponse
from django.db import transaction
import stripe
import requests
from geopy.geocoders import Nominatim
import time
from usuarios.forms import *
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

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

             
               
               
                    
                messages.success(request, 'Cadastro Realizado com sucesso!')
                return redirect('login')
            else:
                print("CEP inválido ou não encontrado")
        else:
            print("Formulário inválido")
            messages.error(request, form.errors)
    
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

def save_with_retry(model_instance, retries=5, delay=1):
    for attempt in range(retries):
        try:
            model_instance.save()
            return  # Sai da função se o save foi bem-sucedido
        except OperationalError:
            if attempt < retries - 1:  # Não é a última tentativa
                time.sleep(delay)  # Espere antes de tentar novamente
            else:
                raise  # Re-lança a exceção na última tentativa


def registerProfissional(request):
    banners = Banner.objects.all()
    especialidades = Especialidade.objects.all().order_by('nome')
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
                user.email = form.cleaned_data['email']
                user.telefone = form.cleaned_data['telefone']
                user.nome = form.cleaned_data['nome']
                user.username = form.cleaned_data['username']
                user.descricao = form.cleaned_data['descricao']
                user.codigo = form.cleaned_data['codigo']
                user.foto = form.cleaned_data['foto']
                user.diploma = form.cleaned_data['diploma']
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

                # Configurando o Stripe
                stripe.api_key = 'sk_test_51O4Zn5DVCQ3YDKzSxKAq7l1zmFFTGkBMy9C8ggrlsXjTD700ekVK2umWAzz6Y0tkXzh2tAD2sUC2t28t0IaGPqPp00tA2BStNs'

                token = request.POST.get('stripeToken')
                try:
                    customer = stripe.Customer.create(
                        source=token,
                        email=request.POST.get('email'),  # substitua por seu campo de email
                    )
                    subscription = stripe.Subscription.create(
                    customer=customer.id,
                    items=[{'plan': 'price_1O6bAWDVCQ3YDKzSh5AaoKKY'}],
                                        )
                except stripe.error.StripeError as e:
                    # Trate os erros do Stripe aqui
                    print(e)
                    return redirect('erro_stripe')  # Redirecione para uma página de erro ou algo assim
                except Exception as e:
                    # Trate outros erros aqui
                    print(e)
                    return redirect('erro_generico')  # Redirecione para uma página de erro ou algo assim

                # Agora crie uma Subscription no seu banco de dados
                profissional_subscription = Subscription(
                    profissional=user,  # Supondo que 'user' seja o seu objeto Profissional
                    stripe_subscription_id=subscription.id,
                )
                profissional_subscription.save()


                messages.success(request, 'Cadastro Realizado com sucesso!')
                return redirect('login')

        else:
            print("Formulário inválido")
            messages.error(request, form.errors)

    context = {
        'especialidades': especialidades,
        'convenios': convenios,
        'idiomas': idiomas,
        'form': form,
        'tipo_profissionais': tipo_profissional,
        'banners':banners
    }

    return render(request, 'core/registroProfissionais.html', context)



def registerClinica(request):
    stripe.api_key = 'sk_test_51O4Zn5DVCQ3YDKzSxKAq7l1zmFFTGkBMy9C8ggrlsXjTD700ekVK2umWAzz6Y0tkXzh2tAD2sUC2t28t0IaGPqPp00tA2BStNs'  # Configuração do Stripe
    banners = Banner.objects.all()
    tipo_clinica = TipoClinica.objects.all()
    especialidades = Especialidade.objects.all()
    idiomas = Idioma.objects.all()
    convenios = Convenio.objects.all()
    tipo_profissional = TipoProfissional.objects.all()
    form = ClinicaForm()

    if request.method == 'POST':
        form = ClinicaForm(request.POST, request.FILES)
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
                            clinica=user
                            
                        )

                        estados.append(estado)
                        cidades.append(cidade)
                        bairros.append(bairro)
                        enderecos.append(endereco)
                        ceps_list.append(cep_obj)

                # Salve o usuário antes de adicionar relações
                user.save()

                user.set_password(form.cleaned_data['password1'])
                user.email = form.cleaned_data['email']
                user.telefone = form.cleaned_data['telefone']
                user.nome = form.cleaned_data['nome']
                user.username = form.cleaned_data['username']
                user.descricao = form.cleaned_data['descricao']
                user.foto = form.cleaned_data['foto']
                selected_tipo_profissional = form.cleaned_data['tipo_profissional']
                selected_tipo_clinica = form.cleaned_data['tipo_clinica']
                selected_especialidades = form.cleaned_data['especialidades']
                selected_convenios = form.cleaned_data['convenios']
                selected_idiomas = form.cleaned_data['idiomas']
              
                
                user.estados.set(estados)
                user.cidades.set(cidades)
                user.bairros.set(bairros)
                user.ceps.set(ceps_list)        
                user.tipo_clinica.set(selected_tipo_clinica)
                user.tipo_profissional.set(selected_tipo_profissional)
                user.especialidades.set(selected_especialidades)
                user.convenios.set(selected_convenios)
                user.idiomas.set(selected_idiomas)
                user.enderecos.set(enderecos)

                token = request.POST.get('stripeToken')  # Obtenção do Token do Stripe

                try:
                    customer = stripe.Customer.create(
                        source=token,
                        email=request.POST.get('email'),  # substitua por seu campo de email
                    )
                    subscription = stripe.Subscription.create(
                        customer=customer.id,
                        items=[{'plan': 'price_1O4ZsHDVCQ3YDKzSRnhIFsCi'}],
                        trial_period_days=30,
                    )
                except stripe.error.StripeError as e:
                    # Trate os erros do Stripe aqui
                    print(e)
                    return redirect('erro_stripe')  # Redirecione para uma página de erro ou algo assim
                except Exception as e:
                    # Trate outros erros aqui
                    print(e)
                    return redirect('erro_generico')  # Redirecione para uma página de erro ou algo assim
                
                # Agora crie uma Subscription no seu banco de dados
                clinica_subscription = Subscription(
                    clinica=user,  # Supondo que 'user' seja o seu objeto Clinica
                    stripe_subscription_id=subscription.id,
                )
                clinica_subscription.save()

                user.save()
                messages.success(request, 'Clínica criada com sucesso!')
                return redirect('login')

        else:
            messages.error(request, form.errors)
            print("Formulário inválido")
            print(form.errors)

    context = {
        'especialidades': especialidades,
        'convenios': convenios,
        'idiomas': idiomas,
        'form': form,
        'tipos_profissionais': tipo_profissional,
        'tipos_clinicas':tipo_clinica,
        'banners':banners
    }

    return render(request, 'core/registroClinicas.html', context)

    




from django.contrib.auth import login as auth_login
from .forms import LoginForm
from django.contrib.auth import authenticate

@csrf_exempt
def user_login(request):
    banners = Banner.objects.all()
    context = {
        'banners': banners,
    }

    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        
        if user is not None:
            auth_login(request, user)
            messages.success(request, "Usuário logado com sucesso!")
            return redirect('home')
        else:
            messages.error(request, "Email ou senha inválidos.")
    else:
        form = LoginForm()
        
    context['form'] = form  # Agora, o form é adicionado ao contexto aqui.
        
    return render(request, 'core/login.html', context)


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
    
    
    
    logging.debug("Iniciando alterar_Profissional")
    logging.debug(f"Data do POST: {request.POST}")
    logging.debug(f"Data dos FILES: {request.FILES}")
    profissional = request.user.profissional
    has_active_subscription = Subscription.objects.filter(Q(profissional=profissional),
        active=True).exists()
    convenios = Convenio.objects.all()
    idiomas = Idioma.objects.all()
    servicos = Servico.objects.all()
    fotos = Foto.objects.all()        
    days_remaining = profissional.get_trial_days_remaining()
    

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
        'has_active_subscription': has_active_subscription,
        'fotos':fotos,
        'days_remaining': days_remaining
        
    })

from django.contrib import messages
from django.core.files.storage import default_storage
from django.contrib import messages
from django.shortcuts import render, redirect
from .forms import ProfissionalForm
from .models import Foto
import logging
logging.basicConfig(level=logging.DEBUG)
def alterar_Profissional(request):
    logging.debug("Iniciando alterar_Profissional")
    logging.debug(f"Data do POST: {request.POST}")
    logging.debug(f"Data dos FILES: {request.FILES}")

    user = request.user.profissional
    has_active_subscription = Subscription.objects.filter(
        Q(profissional=user) & Q(active=True)
    ).exists()
    convenios = Convenio.objects.all()
    idiomas = Idioma.objects.all()
    servicos = Servico.objects.all()
    fotos = Foto.objects.all()
    days_remaining = user.profissional.get_trial_days_remaining()
    form = None
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'update_profile':

            form = ProfissionalForm(request.POST, request.FILES, instance=user)

            if form.is_valid():
                logging.debug("Formulário é válido.")
                cleaned_data = form.cleaned_data
                logging.debug(f"Dados limpos do formulário: {cleaned_data}")

                user.nome = cleaned_data.get('nome', '')
                user.sobrenome = cleaned_data.get('sobrenome', '')
                user.descricao = cleaned_data.get('descricao', '')
                user.telefone = cleaned_data.get('telefone', '')
                user.preco = cleaned_data.get('preco', '')
                user.save()

                user.convenios.set(cleaned_data.get('convenios', []))
                user.idiomas.set(cleaned_data.get('idiomas', []))
                user.servicos.set(cleaned_data.get('servicos', []))

                # Código novo começa aqui
                new_galeria_ids = request.POST.getlist('galeria')  # IDs enviados do frontend
                new_galeria_ids = list(map(int, new_galeria_ids))  # Convertendo para inteiros

                current_galeria_ids = [foto.id for foto in user.galeria.all()]  # IDs atuais no DB

                ids_to_remove = set(current_galeria_ids) - set(new_galeria_ids)  # IDs para remover
                
                for id_to_remove in ids_to_remove:
                    Foto.objects.get(id=id_to_remove).delete()
                # Código novo termina aqui

                new_galeria_entries = []
                if request.FILES.getlist('galeria'):
                    for file in request.FILES.getlist('galeria'):
                        if not file:
                            continue
                        file_name = default_storage.save(file.name, file)
                        new_foto = Foto(imagem=file_name, profissional=user)
                        new_foto.save()
                        new_galeria_entries.append(new_foto)

                with transaction.atomic():
                    user.save()
                    if new_galeria_entries:
                        user.galeria.add(*new_galeria_entries)

                logging.debug(f"Novas entradas na galeria: {new_galeria_entries}")
                logging.debug(f"Fotos na galeria do usuário: {user.galeria.all()}")

                messages.success(request, 'Perfil atualizado com sucesso!')
                return redirect('editar_perfil')
            
        elif action == 'update_photo':
            logging.debug("Formulário iniciado para atualizar foto")
            form = FotoProfForm(request.POST, request.FILES)
            if form.is_valid():
                logging.debug("Formulário é válido.")
                new_foto = form.cleaned_data['foto']
                logging.debug(f"Nova foto obtida: {new_foto}")

                user.foto = new_foto
                user.save()

                messages.success(request, 'Foto de perfil atualizada com sucesso!')
                return redirect('editar_perfil')
        
        elif action == 'responder_pergunta':
            form = RespostaForm(request.POST)
            pergunta_id = request.POST.get('pergunta_id')  # Obtenha o ID da pergunta de alguma forma (campo oculto, por exemplo)
            pergunta = PerguntaResposta.objects.get(id=pergunta_id)

            if form.is_valid():
                resposta = form.cleaned_data['resposta']
                pergunta.resposta = resposta
                pergunta.save()
                messages.success(request, 'Pergunta respondida com sucesso!')
                return redirect('editar_perfil')
            else:
                messages.error(request, 'Erro ao responder pergunta.')
                
                
        elif action == 'update_address':
            form = AddressUpdateForm(request.POST)  # ou outro formulário adequado
            if form.is_valid():
                # Inicia a transação atômica
                with transaction.atomic():
                    # Obtenha as listas de CEPs e Complementos
                    ceps = request.POST.getlist('cep[]')
                    complementos = request.POST.getlist('complemento[]')

                    # Lista para armazenar os objetos criados/obtidos
                    enderecos = []
                    estados = []
                    cidades = []
                    bairros = []
                    ceps_list = []

                    # Itere sobre as listas
                    for i, cep in enumerate(ceps):
                        complemento = complementos[i]

                        # Consulta a API ViaCEP para obter as informações do endereço
                        response = requests.get(f'https://viacep.com.br/ws/{cep}/json/')
                        data = response.json()

                        if response.status_code == 200 and not data.get('erro'):
                            estado, _ = Estado.objects.get_or_create(nome=data['uf'])
                            cidade, _ = Cidade.objects.get_or_create(nome=data['localidade'], estado=estado)
                            bairro, _ = Bairro.objects.get_or_create(nome=data['bairro'], cidade=cidade)
                            cep_obj, _ = CEP.objects.get_or_create(codigo=cep)

                            # Obtenha as coordenadas
                            endereco_completo = f"{data['logradouro']}, {data['bairro']}, {data['localidade']}, {data['uf']}, {data['cep']}"
                            latitude, longitude = obter_coordenadas(endereco_completo, "AIzaSyBLZ8D6WJwaCql2h4-UGjibK4tx9MhZmXE")

                            # Cria o objeto Endereco
                            endereco, _ = Endereco.objects.get_or_create(
                                rua=data['logradouro'],
                                complemento=complemento,
                                bairro=bairro,
                                cidade=cidade,
                                estado=estado,
                                cep=cep_obj,
                                latitude=latitude,
                                longitude=longitude,
                                profissional=user  # Supondo que o usuário é um profissional
                            )

                            # Adiciona os objetos às listas
                            estados.append(estado)
                            cidades.append(cidade)
                            bairros.append(bairro)
                            enderecos.append(endereco)
                            ceps_list.append(cep_obj)

                    # Associa os objetos ao profissional
                    user.estado.set(estados)
                    user.cidade.set(cidades)
                    user.bairro.set(bairros)
                    user.ceps.set(ceps_list)
                    user.enderecos.set(enderecos)

                    # Salva o profissional
                    user.save()

                    messages.success(request, 'Endereço atualizado com sucesso!')
                    return redirect('editar_perfil')
    else:
        logging.debug(f"Formulário não é válido. Erros: {form.errors}")
        messages.error(request, 'Erro na atualização do endereço.')

    logging.debug("Finalizando alterar_Profissional")

    return render(request, 'core/editar_profissional.html', {
        'form': form, 
        'convenios': convenios,
        'idiomas': idiomas,
        'servicos': servicos,
        'fotos': fotos,
        'profissional': user,
        'has_active_subscription': has_active_subscription,
        'days_remaining': days_remaining
  
    })
    
    

        
#EDITAR PERFIL
@login_required
def editar_perfil_clinica(request):
   
    logging.debug("Iniciando alterar_Clinica")
    logging.debug(f"Data do POST: {request.POST}")
    logging.debug(f"Data dos FILES: {request.FILES}")
    clinica = request.user.clinica
    has_active_subscription = Subscription.objects.filter(Q(clinica=clinica),
        active=True).exists()
    convenios = Convenio.objects.all()
    idiomas = Idioma.objects.all()
    servicos = Servico.objects.all()
    fotos = Foto.objects.all()
    days_remaining = clinica.get_trial_days_remaining()

    if request.method == 'POST':
        acao = request.POST.get('acao')
        clinica_form = ClinicaUpdateForm(request.POST, instance=request.user.clinica)
        endereco_form = EnderecoForm(request.POST)
        
        if clinica_form.is_valid():
            clinica_form.save()
        
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
                endereco_instance = Endereco.objects.get(id=endereco_id, clinica=request.user.clinica)
                endereco_form = EnderecoForm(request.POST, instance=endereco_instance)
                if endereco_form.is_valid():
                    endereco_form.save()
                    messages.success(request, 'Endereço atualizado com sucesso.')
            except Endereco.DoesNotExist:
                messages.error(request, 'Endereço não encontrado.')
        
        elif acao == 'excluir':
            endereco_id = request.POST.get('endereco_id')
            try:
                endereco = Endereco.objects.get(id=endereco_id, clinica=request.user.clinica)
                endereco.delete()
                messages.success(request, 'Endereço excluído com sucesso.')
            except Endereco.DoesNotExist:
                messages.error(request, 'Endereço não encontrado.')
    else:
        clinica_form = ClinicaUpdateForm(instance=request.user.clinica)
        endereco_form = EnderecoForm()

    enderecos_da_clinica = Endereco.objects.filter(clinica=request.user.clinica)
    return render(request, 'core/editar_clinica.html', {
        'clinica_form': clinica_form,
        'endereco_form': endereco_form,
        'enderecos': enderecos_da_clinica,
        'convenios':convenios,
        'idiomas':idiomas,
        'servicos':servicos,
        'clinica':clinica,
        'fotos':fotos,
        'has_active_subscription': has_active_subscription,
        'days_remaining': days_remaining
        
    })
        
        

def alterar_Clinica(request):
    logging.debug("Iniciando alterar_Clinica")
    logging.debug(f"Data do POST: {request.POST}")
    logging.debug(f"Data dos FILES: {request.FILES}")

    user = request.user.clinica
    has_active_subscription = Subscription.objects.filter(
        clinica=user, active=True
    ).exists()
    convenios = Convenio.objects.all()
    idiomas = Idioma.objects.all()
    servicos = Servico.objects.all()
    fotos = Foto.objects.all()
    days_remaining = user.clinica.get_trial_days_remaining()
    form = None
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'update_profile':

            form = ClinicaEditarForm(request.POST, request.FILES, instance=user)

            if form.is_valid():
                logging.debug("Formulário é válido.")
                cleaned_data = form.cleaned_data
                logging.debug(f"Dados limpos do formulário: {cleaned_data}")

                user.nome = cleaned_data.get('nome', '')
                user.descricao = cleaned_data.get('descricao', '')
                user.telefone = cleaned_data.get('telefone', '')
                user.save()

                user.convenios.set(cleaned_data.get('convenios', []))
                user.idiomas.set(cleaned_data.get('idiomas', []))
                user.servicos.set(cleaned_data.get('servicos', []))

                # Código novo começa aqui
                new_galeria_ids = request.POST.getlist('galeria')  # IDs enviados do frontend
                new_galeria_ids = list(map(int, new_galeria_ids))  # Convertendo para inteiros

                current_galeria_ids = [foto.id for foto in user.galeria.all()]  # IDs atuais no DB

                ids_to_remove = set(current_galeria_ids) - set(new_galeria_ids)  # IDs para remover
                
                for id_to_remove in ids_to_remove:
                    Foto.objects.get(id=id_to_remove).delete()
                # Código novo termina aqui

                new_galeria_entries = []
                if request.FILES.getlist('galeria'):
                    for file in request.FILES.getlist('galeria'):
                        if not file:
                            continue
                        file_name = default_storage.save(file.name, file)
                        new_foto = Foto(imagem=file_name, clinica=user)
                        new_foto.save()
                        new_galeria_entries.append(new_foto)

                with transaction.atomic():
                    user.save()
                    if new_galeria_entries:
                        user.galeria.add(*new_galeria_entries)

                logging.debug(f"Novas entradas na galeria: {new_galeria_entries}")
                logging.debug(f"Fotos na galeria do usuário: {user.galeria.all()}")

                messages.success(request, 'Perfil atualizado com sucesso!')
                return redirect('editar_clinica')
            
        elif action == 'update_photo':
            logging.debug("Formulário iniciado para atualizar foto")
            form = FotoClinicaForm(request.POST, request.FILES)
            if form.is_valid():
                logging.debug("Formulário é válido.")
                new_foto = form.cleaned_data['foto']
                logging.debug(f"Nova foto obtida: {new_foto}")

                user.foto = new_foto
                user.save()

                messages.success(request, 'Foto de perfil atualizada com sucesso!')
                return redirect('editar_clinica')
        
        elif action == 'responder_pergunta':
            form = RespostaForm(request.POST)
            pergunta_id = request.POST.get('pergunta_id')  # Obtenha o ID da pergunta de alguma forma (campo oculto, por exemplo)
            pergunta = PerguntaResposta.objects.get(id=pergunta_id)

            if form.is_valid():
                resposta = form.cleaned_data['resposta']
                pergunta.resposta = resposta
                pergunta.save()
                messages.success(request, 'Pergunta respondida com sucesso!')
                return redirect('editar_clinica')
            else:
                messages.error(request, 'Erro ao responder pergunta.')
        elif action == 'update_address':
            form = AddressUpdateForm(request.POST)  # ou outro formulário adequado
            if form.is_valid():
                # Inicia a transação atômica
                with transaction.atomic():
                    # Obtenha as listas de CEPs e Complementos
                    ceps = request.POST.getlist('cep[]')
                    complementos = request.POST.getlist('complemento[]')

                    # Lista para armazenar os objetos criados/obtidos
                    enderecos = []
                    estados = []
                    cidades = []
                    bairros = []
                    ceps_list = []

                    # Itere sobre as listas
                    for i, cep in enumerate(ceps):
                        complemento = complementos[i]

                        # Consulta a API ViaCEP para obter as informações do endereço
                        response = requests.get(f'https://viacep.com.br/ws/{cep}/json/')
                        data = response.json()

                        if response.status_code == 200 and not data.get('erro'):
                            estado, _ = Estado.objects.get_or_create(nome=data['uf'])
                            cidade, _ = Cidade.objects.get_or_create(nome=data['localidade'], estado=estado)
                            bairro, _ = Bairro.objects.get_or_create(nome=data['bairro'], cidade=cidade)
                            cep_obj, _ = CEP.objects.get_or_create(codigo=cep)

                            # Obtenha as coordenadas
                            endereco_completo = f"{data['logradouro']}, {data['bairro']}, {data['localidade']}, {data['uf']}, {data['cep']}"
                            latitude, longitude = obter_coordenadas(endereco_completo, "AIzaSyBLZ8D6WJwaCql2h4-UGjibK4tx9MhZmXE")

                            # Cria o objeto Endereco
                            endereco, _ = Endereco.objects.get_or_create(
                                rua=data['logradouro'],
                                complemento=complemento,
                                bairro=bairro,
                                cidade=cidade,
                                estado=estado,
                                cep=cep_obj,
                                latitude=latitude,
                                longitude=longitude,
                                clinica=user  # Supondo que o usuário é um profissional
                            )

                            # Adiciona os objetos às listas
                            estados.append(estado)
                            cidades.append(cidade)
                            bairros.append(bairro)
                            enderecos.append(endereco)
                            ceps_list.append(cep_obj)

                    # Associa os objetos ao profissional
                    user.estados.set(estados)
                    user.cidades.set(cidades)
                    user.bairros.set(bairros)
                    user.ceps.set(ceps_list)
                    user.enderecos.set(enderecos)

                    # Salva o profissional
                    user.save()

                    messages.success(request, 'Endereço atualizado com sucesso!')
                    return redirect('editar_clinica')            
        else:
                logging.debug(f"Formulário não é válido. Erros: {form.errors}")
                messages.error(request, 'Erro na atualização do perfil.')

    logging.debug("Finalizando alterar_Clinica")

    return render(request, 'core/editar_clinica.html', {
        'form': form, 
        'convenios': convenios,
        'idiomas': idiomas,
        'servicos': servicos,
        'fotos': fotos,
        'clinica': user,
        'has_active_subscription': has_active_subscription,
        'days_remaining': days_remaining
  
    })
    
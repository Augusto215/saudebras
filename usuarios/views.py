from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.core.serializers import serialize
from django.core.files.storage import default_storage
from django.db.models import Q
from django.db import IntegrityError, transaction
from django.db import OperationalError
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.contrib.auth import update_session_auth_hash
import logging
import json
import requests
import re
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash, authenticate
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.db import transaction
import json
from django.contrib.auth.forms import PasswordChangeForm
logger = logging.getLogger(__name__)

from django.http import JsonResponse
from django.contrib.auth import authenticate

import stripe
import requests
from geopy.geocoders import Nominatim
import time
from usuarios.forms import *
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404

from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.http import HttpResponse
from django.contrib.auth.tokens import default_token_generator




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

                user = Cliente(
                    nome=form.cleaned_data['nome'],
                    sobrenome=form.cleaned_data['sobrenome'],
                    username = re.sub(r'\D', '', form.cleaned_data['username']),
                    telefone=form.cleaned_data['telefone'],
                    email=form.cleaned_data['email'],
                    foto=form.cleaned_data['foto'],
                    estado=estado,
                    cidade=cidade,
                    bairro=bairro,
                    cep=cep,
                )

                user.set_password(form.cleaned_data['password1'])
                user.save()

                    
                return redirect('sucessoCliente')
               
        else:
            print("Formulário inválido")
            messages.error(request, form.errors)
    
    return render(request, 'core/registroClientes.html', {'form': form})



def redirectCliente(request):
    return render(request, 'core/contacriada.html')


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
                        latitude, longitude = obter_coordenadas(endereco_completo, "AIzaSyCBd2FPXoFej_0ooiHJfRjCZFzIADYSUIY")

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

                user.set_password(form.cleaned_data['password1'])
                user.tipo_profissional = form.cleaned_data['tipo_profissional']
                user.email = form.cleaned_data['email']
                user.telefone = form.cleaned_data['telefone']
                user.nome = form.cleaned_data['nome']
                user.username = re.sub(r'\D', '', form.cleaned_data['username']) 
                user.descricao = form.cleaned_data['descricao']
                user.codigo = form.cleaned_data['codigo']
                user.foto = form.cleaned_data['foto']
                user.diploma = form.cleaned_data['diploma']
                selected_especialidades = form.cleaned_data['especialidades']
                selected_convenios = form.cleaned_data['convenios']
                selected_idiomas = form.cleaned_data['idiomas']

                # Salve o usuário antes de adicionar relações
                user.save()

                user.estado.set(estados)
                user.cidade.set(cidades)
                user.bairro.set(bairros)
                user.ceps.set(ceps_list)
                user.especialidades.set(selected_especialidades)
                user.convenios.set(selected_convenios)
                user.idiomas.set(selected_idiomas)
                user.enderecos.set(enderecos)

                # Configurando o Stripe
                stripe.api_key = 'sk_test_51OUOvLK0evm2fcdGJpwO9LInadGfiwH2U0ftWu4DIQo32A6c5bTeUYwiKmvdSsdL3GhZyjw9p3d75sqzTKHQF0VR001NrAgjhZ'

                # Abordagem simplificada - usar Payment Intent com setup_future_usage
                
                email = request.POST.get('email')
                payment_intent_id = request.POST.get('payment_intent_id')
                
                if not email:
                    print("Erro: Email não encontrado")
                    messages.error(request, 'Email é obrigatório para o pagamento.')
                    return redirect('registerProfissional')
                
                try:
                    customer = None
                    payment_method_id = None
                    
                    if payment_intent_id:
                        # Recuperar o Payment Intent
                        payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
                        
                        # Verificar se o pagamento foi bem-sucedido
                        if payment_intent.status != 'succeeded':
                            raise Exception(f"Payment Intent não foi bem-sucedido: {payment_intent.status}")
                        
                        # Usar o customer do Payment Intent (criado na create_payment_intent)
                        if payment_intent.customer:
                            customer = stripe.Customer.retrieve(payment_intent.customer)
                            
                            # O payment method já deve estar anexado ao customer pelo setup_future_usage
                            if payment_intent.payment_method:
                                payment_method_id = payment_intent.payment_method
                                
                                # Verificar se já está anexado e definir como padrão
                                payment_method = stripe.PaymentMethod.retrieve(payment_method_id)
                                if payment_method.customer == customer.id:
                                    # Definir como método padrão
                                    stripe.Customer.modify(
                                        customer.id,
                                        invoice_settings={
                                            'default_payment_method': payment_method_id
                                        }
                                    )
                    
                    # Se ainda não temos customer, criar um
                    if not customer:
                        customer = stripe.Customer.create(email=email)
                    
                    # Criar subscription
                    subscription_params = {
                        'customer': customer.id,
                        'items': [{'price': 'price_1Rf05cK0evm2fcdG13zQMKIN'}],
                        'expand': ['latest_invoice.payment_intent']
                    }
                    
                    # Se não temos payment method, usar trial
                    if not payment_method_id:
                        subscription_params['trial_period_days'] = 7
                    else:
                        subscription_params['default_payment_method'] = payment_method_id
                    
                    subscription = stripe.Subscription.create(**subscription_params)
                    print(f"Subscription criada: {subscription.id}")
                except Exception as e:
                    # Trate outros erros aqui
                    print(f"Erro genérico: {e}")
                    if request.POST.get('payment_intent_id'):
                        return JsonResponse({'success': False, 'error': str(e)})
                    messages.error(request, f'Erro no processo de pagamento: {str(e)}')
                    return redirect('registerProfissional')
                except stripe.error.StripeError as e:
                    # Trate os erros do Stripe aqui
                    print(f"Erro do Stripe: {e}")
                    if request.POST.get('payment_intent_id'):
                        return JsonResponse({'success': False, 'error': str(e)})
                    messages.error(request, f'Erro no pagamento: {str(e)}')
                    return redirect('registerProfissional')

                # Agora crie uma Subscription no seu banco de dados
                profissional_subscription = Subscription(
                    profissional=user,  # Supondo que 'user' seja o seu objeto Profissional
                    stripe_subscription_id=subscription.id,
                )
                profissional_subscription.save()

                # Verificar se é uma requisição AJAX através do content type ou header
                if request.content_type == 'multipart/form-data' and request.POST.get('payment_intent_id'):
                    return JsonResponse({'success': True, 'redirect_url': '/sucessoCliente/'})
                else:
                    return redirect('sucessoCliente')
        else:
            print("Formulário inválido")
            messages.error(request, form.errors)

    context = {
        'especialidades': especialidades,
        'convenios': convenios,
        'idiomas': idiomas,
        'form': form,
        'tipo_profissionais': tipo_profissional,
        'banners': banners
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
                        latitude, longitude = obter_coordenadas(endereco_completo, "AIzaSyCBd2FPXoFej_0ooiHJfRjCZFzIADYSUIY")
                        
                        
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
                user.username = re.sub(r'\D', '', form.cleaned_data['username'])
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

                # Implementação correta para Payment Intents + Subscriptions
                
                email = request.POST.get('email')
                payment_intent_id = request.POST.get('payment_intent_id')

                if not email:
                    print("Erro: Email não encontrado")
                    messages.error(request, 'Email é obrigatório para o pagamento.')
                    return redirect('registerClinica')

                try:
                    customer = None
                    payment_method_id = None
                    
                    if payment_intent_id:
                        # Recuperar o Payment Intent
                        payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
                        print(f"Payment Intent: {payment_intent.id}, Status: {payment_intent.status}")
                        
                        # Verificar se o pagamento foi bem-sucedido
                        if payment_intent.status != 'succeeded':
                            raise Exception(f"Payment Intent não foi bem-sucedido: {payment_intent.status}")
                        
                        # Se o Payment Intent tem um customer, usar ele
                        if payment_intent.customer:
                            customer = stripe.Customer.retrieve(payment_intent.customer)
                        
                        # Obter o método de pagamento do Payment Intent
                        if payment_intent.payment_method:
                            payment_method_id = payment_intent.payment_method
                    
                    # Se não temos customer, criar um novo
                    if not customer:
                        customer = stripe.Customer.create(
                            email=email,
                        )
                        print(f"Novo customer criado: {customer.id}")
                    
                    # Se temos um payment_method_id do Payment Intent, anexá-lo ao customer
                    if payment_method_id:
                        try:
                            # Anexar o método de pagamento ao customer
                            stripe.PaymentMethod.attach(
                                payment_method_id,
                                customer=customer.id
                            )
                            
                            # Definir como método de pagamento padrão para faturas
                            stripe.Customer.modify(
                                customer.id,
                                invoice_settings={
                                    'default_payment_method': payment_method_id
                                }
                            )
                            print(f"Payment method {payment_method_id} anexado e definido como padrão")
                        except stripe.error.InvalidRequestError as e:
                            # O payment method já pode estar anexado ao customer
                            if "already attached" not in str(e):
                                raise e
                    
                    # Criar subscription com trial e método de pagamento padrão
                    subscription_params = {
                        'customer': customer.id,
                        'items': [{'plan': 'price_1O4ZsHDVCQ3YDKzSRnhIFsCi'}],
                        'trial_period_days': 30,
                        'expand': ['latest_invoice.payment_intent']
                    }
                    
                    # Se temos um payment method, especificá-lo na subscription
                    if payment_method_id:
                        subscription_params['default_payment_method'] = payment_method_id
                    
                    subscription = stripe.Subscription.create(**subscription_params)
                    print(f"Subscription criada: {subscription.id}")
                except stripe.error.StripeError as e:
                    # Trate os erros do Stripe aqui
                    print(f"Erro do Stripe: {e}")
                    messages.error(request, f'Erro no pagamento: {str(e)}')
                    return redirect('registerClinica')
                except Exception as e:
                    # Trate outros erros aqui
                    print(f"Erro genérico: {e}")
                    messages.error(request, f'Erro no processo de pagamento: {str(e)}')
                    return redirect('registerClinica')
                
                # Agora crie uma Subscription no seu banco de dados
                clinica_subscription = Subscription(
                    clinica=user,  # Supondo que 'user' seja o seu objeto Clinica
                    stripe_subscription_id=subscription.id,
                )
                clinica_subscription.save()

                user.save()
                return redirect('sucessoCliente')


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

        print(f"Recebido login: username={username}, password={password}")

        # Verifica se usuário existe
        try:
            user_obj = Cliente.objects.get(email=username)
            print(f"Usuário encontrado no banco: {user_obj}")
        except Cliente.DoesNotExist:
            print("Usuário não encontrado no banco.")

        # Tenta autenticar
        user = authenticate(request, username=username, password=password)

        if user is not None:
            print("Autenticação bem-sucedida")
            auth_login(request, user)
            messages.success(request, "Login realizado com sucesso")
            next_page = request.POST.get('next', 'home')
            return redirect(next_page)
        else:
            print("Falha na autenticação")
            messages.error(request, "Email ou senha inválidos.")
    else:
        form = LoginForm()

    context['form'] = form
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
    logging.debug(f"Método da requisição: {request.method}")
    logging.debug("Iniciando alterar_Profissional")
    if request.method == 'POST':
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

                # Processar campos dinâmicos diretamente do request.POST
                convenios_ids = request.POST.getlist('convenios')
                idiomas_ids = request.POST.getlist('idiomas')  
                servicos_ids = request.POST.getlist('servicos')
                
                logging.debug(f"Convênios IDs: {convenios_ids}")
                logging.debug(f"Idiomas IDs: {idiomas_ids}")
                logging.debug(f"Serviços IDs: {servicos_ids}")

                # Converter para inteiros e filtrar valores vazios
                convenios_ids = [int(id) for id in convenios_ids if id]
                idiomas_ids = [int(id) for id in idiomas_ids if id]
                servicos_ids = [int(id) for id in servicos_ids if id]

                user.convenios.set(convenios_ids)
                user.idiomas.set(idiomas_ids)
                user.servicos.set(servicos_ids)

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
            else:
                logging.debug(f"Formulário não é válido. Erros: {form.errors}")
                messages.error(request, 'Erro ao atualizar perfil. Verifique os dados inseridos.')
            
        elif action == 'update_photo':
            logging.debug("Formulário iniciado para atualizar foto")
            
            # Verificar se um arquivo foi enviado
            if 'foto' not in request.FILES or not request.FILES['foto']:
                messages.error(request, 'Nenhum arquivo foi selecionado. Por favor, escolha uma imagem.')
                return redirect('editar_perfil')
            
            uploaded_file = request.FILES['foto']
            
            # Validações adicionais
            # Verificar tipo de arquivo
            allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif']
            if uploaded_file.content_type not in allowed_types:
                messages.error(request, 'Formato de arquivo não suportado. Use JPG, PNG ou GIF.')
                return redirect('editar_perfil')
            
            # Verificar tamanho do arquivo (5MB máximo)
            max_size = 5 * 1024 * 1024  # 5MB
            if uploaded_file.size > max_size:
                messages.error(request, 'Arquivo muito grande. O tamanho máximo é 5MB.')
                return redirect('editar_perfil')
            
            # Verificar se é realmente uma imagem
            try:
                from PIL import Image  # type: ignore
                import io
                
                # Tentar abrir como imagem
                image = Image.open(io.BytesIO(uploaded_file.read()))
                image.verify()
                
                # Resetar o ponteiro do arquivo
                uploaded_file.seek(0)
                
            except Exception as e:
                logging.error(f"Erro ao validar imagem: {e}")
                messages.error(request, 'O arquivo selecionado não é uma imagem válida.')
                return redirect('editar_perfil')
            
            form = FotoProfForm(request.POST, request.FILES)
            if form.is_valid():
                logging.debug("Formulário é válido.")
                new_foto = form.cleaned_data['foto']
                logging.debug(f"Nova foto obtida: {new_foto}")

                user.foto = new_foto
                user.save()

                messages.success(request, 'Foto de perfil atualizada com sucesso!')
                return redirect('editar_perfil')
            else:
                logging.debug(f"Formulário não é válido. Erros: {form.errors}")
                messages.error(request, 'Erro ao processar a foto. Tente novamente.')
                return redirect('editar_perfil')
        
        elif action == 'update_address':
            logging.debug("Processando atualização/criação de endereço")
            
            cep = request.POST.get('cep', '').replace('-', '')
            rua = request.POST.get('rua', '')
            numero = request.POST.get('numero', '')
            complemento = request.POST.get('complemento', '')
            bairro_nome = request.POST.get('bairro', '')
            cidade_nome = request.POST.get('cidade', '')
            estado_nome = request.POST.get('estado', '')
            endereco_id = request.POST.get('endereco_id', '')
            
            logging.debug(f"Dados recebidos: CEP={cep}, Rua={rua}, Número={numero}")
            
            if not all([cep, rua, bairro_nome, cidade_nome, estado_nome]):
                messages.error(request, 'Todos os campos obrigatórios devem ser preenchidos.')
                return redirect('editar_perfil')
            
            try:
                with transaction.atomic():
                    # Buscar ou criar estado, cidade, bairro e CEP
                    estado, _ = Estado.objects.get_or_create(nome=estado_nome)
                    cidade, _ = Cidade.objects.get_or_create(nome=cidade_nome, estado=estado)
                    bairro, _ = Bairro.objects.get_or_create(nome=bairro_nome, cidade=cidade)
                    cep_obj, _ = CEP.objects.get_or_create(codigo=cep)
                    
                    # Obter coordenadas (opcional)
                    latitude, longitude = None, None
                    try:
                        endereco_completo = f"{rua}, {bairro_nome}, {cidade_nome}, {estado_nome}, {cep}"
                        # latitude, longitude = obter_coordenadas(endereco_completo, "AIzaSyCBd2FPXoFej_0ooiHJfRjCZFzIADYSUIY")
                    except:
                        pass
                    
                    # Criar ou atualizar endereço
                    if endereco_id:
                        # Atualizar endereço existente
                        try:
                            endereco = Endereco.objects.get(id=endereco_id, profissional=user)
                            endereco.rua = rua
                            endereco.numero = int(numero) if numero else None
                            endereco.complemento = complemento
                            endereco.bairro = bairro
                            endereco.cidade = cidade
                            endereco.estado = estado
                            endereco.cep = cep_obj
                            endereco.latitude = latitude
                            endereco.longitude = longitude
                            endereco.save()
                            messages.success(request, 'Endereço atualizado com sucesso!')
                        except Endereco.DoesNotExist:
                            messages.error(request, 'Endereço não encontrado.')
                            return redirect('editar_perfil')
                    else:
                        # Criar novo endereço
                        endereco = Endereco.objects.create(
                            rua=rua,
                            numero=int(numero) if numero else None,
                            complemento=complemento,
                            bairro=bairro,
                            cidade=cidade,
                            estado=estado,
                            cep=cep_obj,
                            latitude=latitude,
                            longitude=longitude,
                            profissional=user
                        )
                        user.enderecos.add(endereco)
                        messages.success(request, 'Endereço adicionado com sucesso!')
                    
                    return redirect('editar_perfil')
                    
            except Exception as e:
                logging.error(f"Erro ao processar endereço: {e}")
                messages.error(request, 'Erro ao processar endereço. Tente novamente.')
                return redirect('editar_perfil')
        
        elif action == 'remove_address':
            logging.debug(f"Removendo endereço - endereco_id: {request.POST.get('endereco_id')}")
            endereco_id = request.POST.get('endereco_id')
            
            if endereco_id:
                try:
                    endereco = Endereco.objects.get(id=endereco_id, profissional=user)
                    logging.debug(f"Endereço encontrado: {endereco}")
                    endereco.delete()
                    logging.debug("Endereço removido com sucesso")
                    messages.success(request, 'Endereço removido com sucesso!')
                except Endereco.DoesNotExist:
                    logging.error(f"Endereço não encontrado - ID: {endereco_id}")
                    messages.error(request, 'Endereço não encontrado.')
                except Exception as e:
                    logging.error(f"Erro ao remover endereço: {e}")
                    messages.error(request, 'Erro ao remover endereço.')
            else:
                logging.error("ID do endereço não fornecido")
                messages.error(request, 'ID do endereço não fornecido.')
            
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
            logging.debug("Processando atualização/criação de endereço")
            
            cep = request.POST.get('cep', '').replace('-', '')
            rua = request.POST.get('rua', '')
            numero = request.POST.get('numero', '')
            complemento = request.POST.get('complemento', '')
            bairro_nome = request.POST.get('bairro', '')
            cidade_nome = request.POST.get('cidade', '')
            estado_nome = request.POST.get('estado', '')
            endereco_id = request.POST.get('endereco_id', '')
            
            logging.debug(f"Dados recebidos: CEP={cep}, Rua={rua}, Número={numero}")
            
            if not all([cep, rua, bairro_nome, cidade_nome, estado_nome]):
                messages.error(request, 'Todos os campos obrigatórios devem ser preenchidos.')
                return redirect('editar_clinica')
            
            try:
                with transaction.atomic():
                    # Buscar ou criar estado, cidade, bairro e CEP
                    estado, _ = Estado.objects.get_or_create(nome=estado_nome)
                    cidade, _ = Cidade.objects.get_or_create(nome=cidade_nome, estado=estado)
                    bairro, _ = Bairro.objects.get_or_create(nome=bairro_nome, cidade=cidade)
                    cep_obj, _ = CEP.objects.get_or_create(codigo=cep)
                    
                    # Obter coordenadas (opcional)
                    latitude, longitude = None, None
                    try:
                        endereco_completo = f"{rua}, {bairro_nome}, {cidade_nome}, {estado_nome}, {cep}"
                        # latitude, longitude = obter_coordenadas(endereco_completo, "AIzaSyCBd2FPXoFej_0ooiHJfRjCZFzIADYSUIY")
                    except:
                        pass
                    
                    # Criar ou atualizar endereço
                    if endereco_id:
                        # Atualizar endereço existente
                        try:
                            endereco = Endereco.objects.get(id=endereco_id, clinica=user)
                            endereco.rua = rua
                            endereco.numero = int(numero) if numero else None
                            endereco.complemento = complemento
                            endereco.bairro = bairro
                            endereco.cidade = cidade
                            endereco.estado = estado
                            endereco.cep = cep_obj
                            endereco.latitude = latitude
                            endereco.longitude = longitude
                            endereco.save()
                            messages.success(request, 'Endereço atualizado com sucesso!')
                        except Endereco.DoesNotExist:
                            messages.error(request, 'Endereço não encontrado.')
                            return redirect('editar_clinica')
                    else:
                        # Criar novo endereço
                        endereco = Endereco.objects.create(
                            rua=rua,
                            numero=int(numero) if numero else None,
                            complemento=complemento,
                            bairro=bairro,
                            cidade=cidade,
                            estado=estado,
                            cep=cep_obj,
                            latitude=latitude,
                            longitude=longitude,
                            clinica=user
                        )
                        user.enderecos.add(endereco)
                        messages.success(request, 'Endereço adicionado com sucesso!')
                    
                    return redirect('editar_clinica')
                    
            except Exception as e:
                logging.error(f"Erro ao processar endereço: {e}")
                messages.error(request, 'Erro ao processar endereço. Tente novamente.')
                return redirect('editar_clinica')
        
        elif action == 'remove_address':
            logging.debug(f"Removendo endereço - endereco_id: {request.POST.get('endereco_id')}")
            endereco_id = request.POST.get('endereco_id')
            
            if endereco_id:
                try:
                    endereco = Endereco.objects.get(id=endereco_id, clinica=user)
                    logging.debug(f"Endereço encontrado: {endereco}")
                    endereco.delete()
                    logging.debug("Endereço removido com sucesso")
                    messages.success(request, 'Endereço removido com sucesso!')
                except Endereco.DoesNotExist:
                    logging.error(f"Endereço não encontrado - ID: {endereco_id}")
                    messages.error(request, 'Endereço não encontrado.')
                except Exception as e:
                    logging.error(f"Erro ao remover endereço: {e}")
                    messages.error(request, 'Erro ao remover endereço.')
            else:
                logging.error("ID do endereço não fornecido")
                messages.error(request, 'ID do endereço não fornecido.')
            
            return redirect('editar_clinica')            
        else:
            # Apenas logar erro se form não for None (ações que usam formulário)
            if form is not None:
                logging.debug(f"Formulário não é válido. Erros: {form.errors}")
                messages.error(request, 'Erro na atualização do perfil.')
            else:
                logging.debug("Ação não reconhecida ou formulário não inicializado")
                messages.error(request, 'Ação não reconhecida.')

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
    
def editar_cliente(request):
    try:
        user = request.user.cliente
        print('cliente encontrado')
        password = user.password
        print(password)
    except:
        print('cliente não encontrado')
        messages.error(request, 'Usuário não encontrado')
        return redirect('home')

    if request.method == 'POST':
        if 'clienteForm' in request.POST:
            cliente_form = ClienteForm(request.POST, instance=user)
            if cliente_form.is_valid():
                cep = cliente_form.cleaned_data['cep']
                response = requests.get(f'https://viacep.com.br/ws/{cep}/json/')
                data = response.json()
                
                if response.status_code == 200 and not data.get('erro'):
                    estado, _ = Estado.objects.get_or_create(nome=data['uf'])
                    cidade, _ = Cidade.objects.get_or_create(nome=data['localidade'], estado=estado)
                    bairro, _ = Bairro.objects.get_or_create(nome=data['bairro'], cidade=cidade)

                    user.estado = estado
                    user.cidade = cidade
                    user.bairro = bairro
                    user.cep = cep
                    user.rua = data['logradouro']
                    
                    cliente_form.save()
                    messages.success(request, 'Perfil atualizado com sucesso!')
                    return redirect('editar_cliente')
                else:
                    messages.error(request, 'CEP inválido')
            else:
                messages.error(request, 'Erro ao atualizar perfil')

        elif 'fotoForm' in request.POST:
            foto_form = FotoForm(request.POST, request.FILES, instance=user)
            if foto_form.is_valid():
                foto_form.save()
                messages.success(request, 'Foto atualizada com sucesso')
                return redirect('editar_cliente')
            else:
                messages.error(request, 'Erro ao atualizar foto')

    else:
        cliente_form = ClienteForm(instance=user)
        foto_form = FotoForm(instance=user)

    context = {
        'cliente_form': cliente_form,
        'foto_form': foto_form
    }
    return render(request, 'core/editar_perfil.html', context)

def editar_senha(request):
    try:
        user = request.user.cliente
        print('cliente encontrado')
    except:
        print('cliente não encontrado')
        messages.error(request, 'Usuário não encontrado')
        return redirect('home')

    logger.info("Acessando a função editar_senha.")
    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        logger.info("Método POST detectado.")

        if not request.user.check_password(current_password):
            logger.warning("Senha atual incorreta.")
            messages.error(request, 'Senha atual incorreta.')
            return redirect('editar_cliente')

        if new_password != confirm_password:
            logger.warning("As novas senhas não coincidem.")
            messages.error(request, 'As novas senhas não coincidem.')
            return redirect('editar_cliente')

        if not new_password or not confirm_password:
            logger.warning("Nova senha não pode ser vazia.")
            messages.error(request, 'Nova senha não pode ser vazia.')
            return redirect('editar_cliente')

        request.user.set_password(new_password)
        request.user.save()
        update_session_auth_hash(request, request.user)  # Importante para manter o usuário logado
        messages.success(request, 'Sua senha foi alterada com sucesso!')
        return redirect('editar_cliente')
    
    logger.info("Método GET detectado.")
    context = {
        'cliente_form': ClienteForm(instance=request.user.cliente),
        'foto_form': FotoForm(instance=request.user.cliente)
    }
    return render(request, 'core/editar_perfil.html', context)

@csrf_exempt
def validate_password(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        current_password = data.get('current_password')
        user = authenticate(username=request.user.username, password=current_password)
        if user is not None:
            return JsonResponse({'valid': True})
        else:
            return JsonResponse({'valid': False})
    return JsonResponse({'valid': False}, status=400)

from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

@staff_member_required
@require_http_methods(["POST"])
def cleanup_invalid_subscriptions(request):
    """
    View administrativa para limpar assinaturas inválidas
    Apenas usuários staff podem executar esta ação
    """
    try:
        from usuarios.models import Subscription
        count_cleaned = Subscription.cleanup_invalid_subscriptions()
        return JsonResponse({
            'success': True,
            'message': f'{count_cleaned} assinaturas inválidas foram limpas'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

def check_subscription_health(request):
    """
    View para verificar a saúde das assinaturas
    Pode ser usada por administradores para monitoramento
    """
    if not request.user.is_staff:
        return JsonResponse({'error': 'Acesso negado'}, status=403)
    
    try:
        from usuarios.models import Subscription
        total_subscriptions = Subscription.objects.filter(active=True).count()
        invalid_count = 0
        
        for subscription in Subscription.objects.filter(active=True):
            if not subscription.validate_stripe_subscription():
                invalid_count += 1
        
        return JsonResponse({
            'total_active_subscriptions': total_subscriptions,
            'invalid_subscriptions_found': invalid_count,
            'health_status': 'healthy' if invalid_count == 0 else 'needs_attention'
        })
    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=500)
import requests
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.http import HttpResponse
from usuarios.models import *
from django.db.models import Exists, OuterRef
from django.db.models import Q
from django.views.decorators.http import require_POST

import logging

import http
from usuarios.forms import *
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import json
from django.db.models import Count, Avg

def nav(request):
    print(request.user)  # Veja qual é o usuário atual
    is_profissional = hasattr(request.user, 'profissional')
    print(is_profissional)
    # Isso deve imprimir True ou False
        
    context = {'is_profissional': is_profissional}
    
    return render(request, 'core/base.html', context)


def home_view(request):
    especialidades = Especialidade.objects.all()
    print(request.user)  # Veja qual é o usuário atual
    is_profissional = hasattr(request.user, 'profissional')
    print(is_profissional)  # Isso      
    context = {
        'especialidades':especialidades
    }
    
    return render(request, 'core/index.html', context)

from django.http import JsonResponse
from usuarios.models import Profissional  

from usuarios.forms import AvaliacaoForm  # Certifique-se de que o caminho para importar o AvaliacaoForm está correto

from django.contrib.contenttypes.models import ContentType

import stripe
from django.views.decorators.csrf import csrf_exempt


logging.basicConfig(level=logging.INFO)

stripe.api_key = "sk_test_51O4Zn5DVCQ3YDKzSxKAq7l1zmFFTGkBMy9C8ggrlsXjTD700ekVK2umWAzz6Y0tkXzh2tAD2sUC2t28t0IaGPqPp00tA2BStNs"

def create_subscription(request):
    YOUR_DOMAIN = "https://saudebras.onrender.com/"
    checkout_session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[
            {
                'price': 'price_1O4ZsHDVCQ3YDKzSRnhIFsCi',
                'quantity': 1,
            },
        ],
        mode='subscription',
        success_url=YOUR_DOMAIN + '/success/',
        cancel_url=YOUR_DOMAIN + '/cancel/',
    )
    return redirect(checkout_session.url)

@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, 'whsec_w0jz4yyortYV9uZlpkSjr66lEJs68RLT'
        )
    except ValueError as e:
        # Invalid payload
        print("Invalid payload")
        raise e
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        print("Invalid signature")
        raise e

    # Handle subscription events
    if event['type'] == 'customer.subscription.created':
        handle_subscription_created(event)
    elif event['type'] == 'customer.subscription.deleted':
        handle_subscription_deleted(event)

    return HttpResponse(status=200)

def handle_subscription_created(event):
    subscription_id = event['data']['object']['id']
    subscription = Subscription.objects.get(stripe_subscription_id=subscription_id)
    subscription.active = True
    subscription.save()

def handle_subscription_deleted(event):
    subscription_id = event['data']['object']['id']
    subscription = Subscription.objects.get(stripe_subscription_id=subscription_id)
    subscription.active = False
    subscription.save()

def success_view(request):
    return render(request, 'core/success.html')

def cancel_view(request):
    return render(request, 'core/cancel.html')




def calcular_media(objeto, Modelo):
    media = Avaliacao.objects.filter(
        content_type=ContentType.objects.get_for_model(Modelo),
        object_id=objeto.id
    ).aggregate(Avg('rating'))
    return media['rating__avg']


def total_avaliacoes(objeto, Modelo):
    return Avaliacao.objects.filter(
        content_type=ContentType.objects.get_for_model(Modelo),
        object_id=objeto.id
    ).count()

def calculate_stars(media):
    if media is None:
        return ["empty"] * 5
    full_stars = int(media)
    half_star = 0 if media == full_stars else 1
    empty_stars = 5 - full_stars - half_star
    return ["full"] * full_stars + ["half"] * half_star + ["empty"] * empty_stars

def perfil_profissional(request, profissional_id):
    profissional = get_object_or_404(Profissional, id=profissional_id)
    media = calcular_media(profissional, Profissional)
    stars = calculate_stars(media)
    total_av = total_avaliacoes(profissional, Profissional)
    is_cliente = hasattr(request.user, 'cliente')
    
    avaliacoes_list = Avaliacao.objects.filter(
        content_type=ContentType.objects.get_for_model(profissional),
        object_id=profissional.id
    )
    
    paginator = Paginator(avaliacoes_list, 5)
    page = request.GET.get('page')
    avaliacoes = paginator.get_page(page)
    perguntas_list = profissional.perguntas.exclude(resposta__isnull=True).exclude(resposta__exact='')
    paginator_perguntas = Paginator(perguntas_list, 5)  # 5 perguntas por página
    page_perguntas = request.GET.get('page_perguntas')
    perguntas_paginated = paginator_perguntas.get_page(page_perguntas)
    form = AvaliacaoForm()  # Inicialização aqui
    form_perguntas = PerguntaRespostaForm()  
    if request.method == 'POST':
        action = request.POST.get('action')
        

        if action == 'send_avaliacao':
            if request.method == 'POST':
                form = AvaliacaoForm(request.POST)
                if form.is_valid():
                    avaliacao = form.save(commit=False)
                    avaliacao.cliente = request.user.cliente
                    avaliacao.content_type = ContentType.objects.get_for_model(profissional)
                    avaliacao.object_id = profissional.id
                    avaliacao.save()
                    media = calcular_media(profissional, Profissional)
                    total_av += 1
                else:
                    print(form.errors)
        elif action == 'send_pergunta':
            form_perguntas = PerguntaRespostaForm(request.POST)
            if form_perguntas.is_valid():
                pergunta = form_perguntas.save(commit=False)
                pergunta.cliente = request.user.cliente
                pergunta.content_type = ContentType.objects.get_for_model(Profissional)
                pergunta.save()  # Primeiro salve o objeto
                profissional.perguntas.add(pergunta)
                
    else:
        form = AvaliacaoForm()
        form_perguntas = PerguntaRespostaForm()
    

    
    if request.META.get('HTTP_ACCEPT') == 'application/json':
        avaliacoes_json = [
            {
                'nome': a.cliente.nome,
                'descricao': a.descricao,
                'rating': a.rating,
                'cliente': {
                    'foto': {
                        'url': a.cliente.foto.url if a.cliente.foto else None,
                    }
                  
                }
            } for a in avaliacoes
        ]
        
        perguntas_json = [
        {
            'pergunta': p.pergunta,
            'nome': p.cliente.nome,
            'resposta':p.resposta,
            # ... outros campos que você quer enviar
        } for p in perguntas_paginated 
    ]
        return JsonResponse({
        'avaliacoes': avaliacoes_json,
        'perguntas': perguntas_json,
        'has_next_avaliacoes': avaliacoes.has_next(),
        'current_page': avaliacoes.number,
        'has_next_perguntas': perguntas_paginated.has_next()
    })

    context = {
        'profissional': profissional,
        'form': form,
        'is_cliente': is_cliente,
        'media': media,
        'total_avaliacoes': total_av,
        'avaliacoes': avaliacoes,
        'stars': stars,
        'form_perguntas': form_perguntas,
        'perguntas_paginated': perguntas_paginated
    }

    return render(request, 'core/perfil_profissional.html', context)

def perfil_clinica(request, clinica_id):
    
    
    clinica = get_object_or_404(Clinica, id=clinica_id)
    has_emergency = clinica.tipo_clinica.filter(nome__icontains='Emergência').exists()
    is_cliente = isinstance(request.user, Cliente)
    avaliacoes = Avaliacao.objects.filter(
        content_type=ContentType.objects.get_for_model(clinica),
        object_id=clinica.id
    )
    
    # Calculando valores aqui para evitar redundância
    media = calcular_media(clinica, Clinica)
    stars = calculate_stars(media)
    total_av = total_avaliacoes(clinica, Clinica)  # Renomeado para evitar conflito com a função
    
    is_cliente = hasattr(request.user, 'cliente')
    
    avaliacoes_list = Avaliacao.objects.filter(
        content_type=ContentType.objects.get_for_model(clinica),
        object_id=clinica.id
    )
    
    paginator = Paginator(avaliacoes_list, 5)
    page = request.GET.get('page')
    avaliacoes = paginator.get_page(page)
    perguntas_list = clinica.perguntas.exclude(resposta__isnull=True).exclude(resposta__exact='')
    paginator_perguntas = Paginator(perguntas_list, 5)  # 5 perguntas por página
    page_perguntas = request.GET.get('page_perguntas')
    perguntas_paginated = paginator_perguntas.get_page(page_perguntas)
    form = AvaliacaoForm()  # Inicialização aqui
    form_perguntas = PerguntaRespostaForm()  
    if request.method == 'POST':
        action = request.POST.get('action')
        action = request.POST.get('action')
        
        
        if action == 'send_avaliacao':
            form = AvaliacaoForm(request.POST)
            avaliacao = form.save(commit=False)
            avaliacao.cliente = request.user.cliente  # Assumindo que o cliente é o usuário logado
            avaliacao.content_type = ContentType.objects.get_for_model(clinica)
            avaliacao.object_id = clinica.id
            avaliacao.save()
            
            # Recalcular a média após nova avaliação
            media = calcular_media(clinica, Clinica)
            total_av += 1  # Atualizar o número total de avaliações
            
            

    
        elif action == 'send_pergunta':
            form_perguntas = PerguntaRespostaForm(request.POST)
            if form_perguntas.is_valid():
                pergunta = form_perguntas.save(commit=False)
                pergunta.cliente = request.user.cliente
                pergunta.content_type = ContentType.objects.get_for_model(clinica)
                pergunta.save()
                clinica.perguntas.add(pergunta)
                
    else:
        form = AvaliacaoForm()
        form_perguntas = PerguntaRespostaForm()
        
            
            
    if request.META.get('HTTP_ACCEPT') == 'application/json':
        avaliacoes_json = [
            {
                'nome': a.cliente.nome,
                'descricao': a.descricao,
                'rating': a.rating,
                'cliente': {
                    'foto': {
                        'url': a.cliente.foto.url if a.cliente.foto else None,
                    }
                
                }
            } for a in avaliacoes
        ]
        
        perguntas_json = [
        {
            'pergunta': p.pergunta,
            'nome': p.cliente.nome,
            'resposta':p.resposta,
            # ... outros campos que você quer enviar
        } for p in perguntas_paginated if p.resposta
    ]
        return JsonResponse({
        'avaliacoes': avaliacoes_json,
        'perguntas': perguntas_json,
        'has_next_avaliacoes': avaliacoes.has_next(),
        'has_next_perguntas': perguntas_paginated.has_next()
    })
                
    context = {
        'clinica': clinica,
        'is_cliente':is_cliente,
        'form': form,
        'is_cliente': is_cliente,
        'has_emergency': has_emergency,
        'media': media,
        'form_perguntas': form_perguntas,
        'perguntas_paginated': perguntas_paginated,
        'avaliacoes': avaliacoes,
        'total_avaliacoes': total_av,  # Usando total_av aqui
        'stars': stars
    }

    return render(request, 'core/perfil_clinica.html', context)




def buscar_profissionais_por_tipo_clinica(request):
    
    q_objects = Q()
    query = request.GET.get('query', '')
    tipo_clinica = request.GET.get('tipo_clinica', None)

    q_objects = Q(is_active=True) & Q(email_verified=True)

    if tipo_clinica:
        q_objects &= Q(tipo_clinica__nome__icontains=tipo_clinica)

    clinicas_ativas = Clinica.objects.filter(q_objects).prefetch_related('tipo_profissional')
    profissionais_ativos = set([tipo_prof.nome for clinica in clinicas_ativas for tipo_prof in clinica.tipo_profissional.all()])
    profissionais_filtrados = [tipo_profissional for tipo_profissional in profissionais_ativos if query.lower() in tipo_profissional.lower()]

    return JsonResponse({'profissionais': sorted(profissionais_filtrados)})


def buscar_especialidades_por_tipo_clinica(request):
    tipo_clinica = request.GET.get('tipo_clinica', None)
    tipo_profissional = request.GET.get('tipo_profissional', None)

    q_objects_clinicas = Q(is_active=True) & Q(email_verified=True)

    if tipo_clinica:
        q_objects_clinicas &= Q(tipo_clinica__nome__icontains=tipo_clinica)

    if tipo_profissional:
        q_objects_clinicas &= Q(tipo_profissional__nome__in=[tipo_profissional])

    clinicas_ativas = Clinica.objects.filter(q_objects_clinicas).prefetch_related('tipo_profissional')

    # Utilizar os IDs das clínicas ativas para filtrar as especialidades
    ids_clinicas_ativas = clinicas_ativas.values_list('id', flat=True)
    especialidades = Especialidade.objects.filter(clinica__id__in=ids_clinicas_ativas)
    
    especialidades_unicas = set(espec.nome for espec in especialidades) 

    especialidades_filtradas = sorted(list(especialidades_unicas))
    
    return JsonResponse({'especialidades': sorted(especialidades_filtradas)})

from django.db.models import Prefetch

def buscar_estados_por_tipo_clinica(request):
    q_objects = Q()
    query = request.GET.get('query', '')
    tipo_clinica = request.GET.get('tipo_clinica', None)
    tipo_profissional = request.GET.get('tipo_profissional', None)
    especialidade = request.GET.get('especialidade', None)

    q_objects = Q(is_active=True) & Q(email_verified=True)

    if tipo_clinica:
        q_objects &= Q(tipo_clinica__nome__icontains=tipo_clinica)

    clinicas_ativas = Clinica.objects.filter(q_objects).prefetch_related('estados', 'tipo_profissional', 'especialidades')

    if especialidade:
        clinicas_ativas = clinicas_ativas.filter(especialidades__nome__icontains=especialidade)
    
    estados_ativos = set([estado.nome for clinica in clinicas_ativas for estado in clinica.estados.all()])
    estados_filtrados = [estado for estado in estados_ativos if query.lower() in estado.lower()]

    return JsonResponse({'estados': sorted(estados_filtrados)})

# Buscar cidades por tipo de clínica
def buscar_cidades_por_tipo_clinica(request):
    q_objects = Q(is_active=True) & Q(email_verified=True)
    
    tipo_clinica = request.GET.get('tipo_clinica', None)
    estado_nome = request.GET.get('estados', None)
    tipo_profissional = request.GET.get('tipo_profissional', None)
    
    cidades = set()

    # Pega o objeto Estado baseado no nome do estado fornecido
    try:
        estado_obj = Estado.objects.get(nome__iexact=estado_nome)
    except Estado.DoesNotExist:
        return JsonResponse({'cidades': []})

    # Filtra as clínicas com base nos critérios
    if tipo_clinica:
        q_objects &= Q(tipo_clinica__nome__icontains=tipo_clinica)
    if tipo_profissional:
        q_objects &= Q(tipo_profissional__nome__icontains=tipo_profissional)

    clinicas_ativas = Clinica.objects.filter(q_objects).prefetch_related('cidades', 'estados')

    # Filtra as cidades baseado no estado
    for clinica in clinicas_ativas:
        for cidade in clinica.cidades.filter(estado=estado_obj).all():
            cidades.add(cidade.nome)
            
    return JsonResponse({'cidades': sorted(list(cidades))})

def buscar_convenios_por_tipo_clinica(request):
    q_objects = Q(is_active=True) & Q(email_verified=True)
    especialidade = request.GET.get('especialidade', None)
    tipo_clinica = request.GET.get('tipo_clinica', None)
    estado_nome = request.GET.get('estados', None)
    tipo_profissional = request.GET.get('tipo_profissional', None)
    cidade_nome = request.GET.get('cidade', None)  # novo campo

    convenios = set()

    # Filtra as clínicas com base nos critérios
    if especialidade:
        q_objects &= Q(especialidades__nome__icontains=especialidade)
    if tipo_clinica:
        q_objects &= Q(tipo_clinica__nome__icontains=tipo_clinica)
    if estado_nome:
        q_objects &= Q(estados__nome__icontains=estado_nome)
    if tipo_profissional:
        q_objects &= Q(tipo_profissional__nome__icontains=tipo_profissional)
    if cidade_nome:
        q_objects &= Q(cidades__nome__icontains=cidade_nome)  # nova condição

    clinicas_ativas = Clinica.objects.filter(q_objects).prefetch_related('convenios', 'estados')

    # Filtra os convênios
    for clinica in clinicas_ativas:
        for convenio in clinica.convenios.all():
            convenios.add(convenio.nome)

    return JsonResponse({'convenios': sorted(list(convenios))})


def buscar_estados(request):
    q_objects = Q(is_active=True) & Q(email_verified=True)
    especialidade = request.GET.get('especialidade', None)

    if especialidade:
        q_objects &= Q(especialidades__nome__icontains=especialidade)
    
    profissionais_ativos = Profissional.objects.filter(q_objects).prefetch_related('estado')
    estados_ativos = set()

    for prof in profissionais_ativos:
        for estado in prof.estado.all():
            estados_ativos.add(estado.nome)
            
    estados_ordenados = sorted(estados_ativos)
        
    return JsonResponse({'estados': list(estados_ordenados)})




def get_cities(request):
    state_name = request.GET.get('estado', None)
    tipo_profissional = request.GET.get('tipo_profissional', None)
    especialidade_query = request.GET.get('especialidade', None)

    q_objects = Q(is_active=True) & Q(email_verified=True)

    if tipo_profissional:
        q_objects &= Q(tipo_profissional=tipo_profissional)

    if state_name:
        profissionais_ativos = Profissional.objects.filter(q_objects).prefetch_related('estado', 'cidade')
        cities = set()

        for profissional in profissionais_ativos:
            for estado in profissional.estado.all():
                if estado.nome == state_name:
                    for cidade in profissional.cidade.all():
                        if cidade.estado.nome == state_name:
                            if especialidade_query:
                                for especialidade in profissional.especialidades.all():
                                    if especialidade.nome == especialidade_query:
                                        cities.add(cidade.nome)
                                        break
                            else:
                                cities.add(cidade.nome)
        cidades_ordenadas = sorted(cities)    
        return JsonResponse({'cities': list(cidades_ordenadas)})
    else:
        return JsonResponse({'cities': []})



def buscar_convenios_por_tipo_profissional(request):
    state_name = request.GET.get('estado', None)
    tipo_profissional = request.GET.get('tipo_profissional', None)
    especialidade_query = request.GET.get('especialidade', None)
    city_name = request.GET.get('cidade', None)  # novo campo

    q_objects = Q(is_active=True) & Q(email_verified=True)

    if tipo_profissional:
        q_objects &= Q(tipo_profissional=tipo_profissional)

    if state_name:
        estado = Estado.objects.get(nome=state_name)
        q_objects &= Q(estado=estado)

    if city_name:
        cidade = Cidade.objects.get(nome=city_name)
        q_objects &= Q(cidade=cidade)  # nova condição

    if especialidade_query:
        q_objects &= Q(especialidades__nome__icontains=especialidade_query)

    profissionais_ativos = Profissional.objects.filter(q_objects).prefetch_related('especialidades', 'convenios')

    convenios = set()

    for profissional in profissionais_ativos:
        for convenio in profissional.convenios.all():
            convenios.add(convenio.nome)

    return JsonResponse({'convenios': list(convenios)})



from django.shortcuts import render


def get_avaliacao_stats(profissional):
    media = calcular_media(profissional, Profissional)
    total_av = total_avaliacoes(profissional, Profissional)
    stars = calculate_stars(media)
    
    return {
        'media': media,
        'total_avaliacoes': total_av,
        'stars': stars
    }

def listar_profissionais(request):
    q_objects = Q(is_active=True, email_verified=True)

    # Debug: Imprimindo para verificar se há alguma média geral
    avaliacoes = Avaliacao.objects.aggregate(media=Avg('rating'))
    print("Media Geral:", avaliacoes)

    # Seus códigos de filtros aqui...
    especialidade = request.GET.get('especialidade', None)
    estado = request.GET.get('estado', None)
    tipo_profissional = request.GET.get('tipo_profissional', None)
    bairros = request.GET.getlist('bairro', None)
    cidade = request.GET.get('cidade', None)
    convenios = request.GET.get('convenios', None)

    if tipo_profissional:
        q_objects &= Q(tipo_profissional=tipo_profissional)
    if especialidade:
        q_objects &= Q(especialidades__nome__icontains=especialidade)
    if estado:
        q_objects &= Q(estado__nome__icontains=estado)
    if cidade:
        q_objects &= Q(cidade__nome__icontains=cidade)
    if bairros:
        q_objects &= Q(bairro__nome__in=bairros)
    if convenios:
        q_objects &= Q(convenios__nome__icontains=convenios)

    queryset = Profissional.objects.filter(q_objects).annotate(
        media=Avg('avaliacoes__rating'),
        total_avaliacoes=Count('avaliacoes')
    ).order_by('nome')

    paginator = Paginator(queryset, 10)
    page = request.GET.get('page')
    context = {}

    try:
        profissionais = paginator.page(page)

        context = {
            'avaliacao': avaliacoes['media'],
            'profissionais': profissionais
            # ... (outros contextos necessários)
        }
        
    except PageNotAnInteger:
        # Se a página não for um inteiro, entregar a primeira página.
        profissionais = paginator.page(1)
        context = {'profissionais': profissionais, 'avaliacao': avaliacoes['media']}

    except EmptyPage:
        # Se a página estiver fora do intervalo, entregar a última página de resultados.
        profissionais = paginator.page(paginator.num_pages)
        context = {'profissionais': profissionais, 'avaliacao': avaliacoes['media']}

    return render(request, 'core/listar_profissionais.html', context)



def get_enderecos(request):
    active_professionals = Profissional.objects.filter(is_active=True, email_verified=True).values('id', 'enderecos__latitude', 'enderecos__longitude')
    return JsonResponse(list(active_professionals), safe=False)


def get_enderecos_clinica(request):
    active_clinicas = Clinica.objects.filter(is_active=True, email_verified=True).values('id', 'enderecos__latitude', 'enderecos__longitude')
    return JsonResponse(list(active_clinicas), safe=False)



def listar_clinicas(request):
    # Inicializa a query com a condição de que os profissionais sejam ativos e verificados por email
    q_objects = Q(is_active=True, email_verified=True)
    
    tipo_clinica = request.GET.get('tipo_clinica', None)
    especialidade = request.GET.get('especialidade', None)
    estados = request.GET.get('estados', None)
    tipo_profissional = request.GET.get('tipo_profissional', None)
    bairros = request.GET.getlist('bairro', None)  # Obtém uma lista de bairros
    cidades = request.GET.get('cidades', None)
    convenios = request.GET.get('convenios', None)
    
    if tipo_clinica:
        q_objects &= Q(tipo_clinica__nome__icontains=tipo_clinica)
    
    if tipo_profissional:
        q_objects &= Q(tipo_profissional__nome__icontains=tipo_profissional)
    
    if especialidade:
        q_objects &= Q(especialidades__nome__icontains=especialidade)
        
    if estados:
        q_objects &= Q(estados__nome__icontains=estados)
    
    if cidades:
        q_objects &= Q(cidades__nome__icontains=cidades)
        

    if bairros:
        q_objects &= Q(bairro__nome__in=bairros)
        
    if convenios:
        q_objects &=Q(convenios__nome__icontains=convenios)
        
    # Debug: Calculando a média geral e o total de avaliações
    avaliacoes = Clinica.objects.aggregate(media=Avg('avaliacoes__rating'), total_avaliacoes=Count('avaliacoes'))
    print("Média Geral das Clínicas:", avaliacoes)
    
    # Filtra e anota o queryset
    queryset = Clinica.objects.filter(q_objects).annotate(
        media=Avg('avaliacoes__rating'),  # Média das avaliações para cada clínica
        total_avaliacoes=Count('avaliacoes')  # Total de avaliações para cada clínica
    ).order_by('nome')
    
    # Anotações adicionais (para o has_emergency)
    has_emergency_subquery = Clinica.tipo_clinica.through.objects.filter(
        clinica_id=OuterRef('id'),
        tipoclinica__nome__icontains='Emergência'
    )
    queryset = queryset.annotate(has_emergency=Exists(has_emergency_subquery))
    
    # Cria um paginador
    paginator = Paginator(queryset, 10)
    page = request.GET.get('page')
    
    try:
        clinicas = paginator.page(page)
    except PageNotAnInteger:
        clinicas = paginator.page(1)
    except EmptyPage:
        clinicas = paginator.page(paginator.num_pages)
    
    context = {
        'clinicas': clinicas,
        'avaliacao': avaliacoes['media'],
        'total_avaliacoes': avaliacoes['total_avaliacoes']
    }
    
    return render(request, 'core/listar_clinicas.html', context)
    



def buscar_tipos_clinicas(request):
    q_objects = Q(is_active=True) & Q(email_verified=True)

    clinicas_ativas = Clinica.objects.filter(q_objects)
    tipos_clinica_ativos = set()

    for clinica in clinicas_ativas:
        for tipo_clinica in clinica.tipo_clinica.all():  # acessando o ManyToMany field
            tipos_clinica_ativos.add(tipo_clinica.nome)

    return JsonResponse({'tipos_clinicas': list(tipos_clinica_ativos)})




def pesquisarProfissionais(request, tipo_profissional=None):
    if tipo_profissional == 'Medico':
        return render(request, 'core/pesquisar/pesquisarMedicos.html')
    elif tipo_profissional == 'Dentista':
        return render(request, 'core/pesquisar/pesquisarDentistas.html')
    else:
        return render(request, 'core/listar_profissionais')
    
    
    
def pesquisarProfissionais(request, tipo_profissional=None):
    if tipo_profissional == 'Médico':
        return render(request, 'core/pesquisar/pesquisarMedicos.html')
    elif tipo_profissional == 'Dentista':
        return render(request, 'core/pesquisar/pesquisarDentistas.html')
    else:
        return render(request, 'core/listar_profissionais')
    

def pesquisarClinicas(request, tipo_clinica=None):
    if tipo_clinica == 'Emergência':
        return render(request, 'core/pesquisar/pesquisarEmergencias.html')
    elif tipo_clinica == 'Clínica':
        return render(request, 'core/pesquisar/pesquisarExames.html')
    else:
        return render(request, 'core/listar_profissionais')
    
    
    

def get_especialidades(request):
    query = request.GET.get('query', '')
    estado = request.GET.get('estado', None)
    tipo_profissional = request.GET.get('tipo_profissional', None)  # novo campo

    q_objects = Q(is_active=True) & Q(email_verified=True)

    if estado:
        q_objects &= Q(estado__nome__icontains=estado)
    if tipo_profissional:  # novo condicional
        q_objects &= Q(tipo_profissional=tipo_profissional)

    profissionais_ativos = Profissional.objects.filter(q_objects).prefetch_related('especialidades')
    especialidades_ativas = set()

    for profissional in profissionais_ativos:
        for especialidade in profissional.especialidades.all():
            especialidades_ativas.add(especialidade.nome)

    especialidades_filtradas = [especialidade for especialidade in especialidades_ativas if query.lower() in especialidade.lower()]

    return JsonResponse({'especialidades': sorted(especialidades_filtradas)})


    
def buscar_tipos_profissionais(request):
    q_objects = Q(is_active=True) & Q(email_verified=True)

    profissionais_ativos = Profissional.objects.filter(q_objects).only('tipo_profissional')
    tipos_ativos = set([prof.tipo_profissional for prof in profissionais_ativos if prof.tipo_profissional])

    return JsonResponse({'tipos_profissionais': list(tipos_ativos)})


def get_states(request):
    states = Estado.objects.all().values_list('nome', flat=True)
    return JsonResponse({'states': list(states)})


    
def buscar_nomes(request):
    query = request.GET.get('query', '')
    
    q_objects = Q(is_active=True) & Q(email_verified=True)
    
    profissionais_ativos = Profissional.objects.filter(q_objects)
    nomes_ativos = set([prof.nome for prof in profissionais_ativos if prof.nome])

    nomes_filtrados = [nome for nome in nomes_ativos if query.lower() in nome.lower()]
    
    return JsonResponse({'nomes': nomes_filtrados})

def buscar_tipos(request):
    query = request.GET.get('query', '')
    q_objects = Q(is_active=True) & Q(email_verified=True)
    
    profissionais_ativos = Profissional.objects.filter(q_objects)
    tipos_ativos = set([prof.tipo_profissional for prof in profissionais_ativos if prof.tipo_profissional])

    tipos_filtrados = [tipo for tipo in tipos_ativos if query.lower() in tipo.lower()]
    
    return JsonResponse({'tipos': tipos_filtrados})

from django.http import JsonResponse, HttpResponseServerError
import logging

logger = logging.getLogger(__name__)

def buscar_bairros(request):
    estado = request.GET.get('estado')
    especialidade = request.GET.get('especialidade')
    
    bairros = Profissional.objects.filter(
        estado__nome=estado, 
        especialidades__nome=especialidade  # Troquei o campo 'especialidade' por 'especialidades__nome'
    ).values('bairro__nome').distinct()  # Troquei o campo 'bairro' por 'bairro__nome'
    
    bairros_list = [b['bairro__nome'] for b in bairros]  # Extração dos nomes dos bairros
    return JsonResponse({'bairros': bairros_list})  
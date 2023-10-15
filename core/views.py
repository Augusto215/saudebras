import requests
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from usuarios.models import *
from django.db.models import Exists, OuterRef
from django.db.models import Q
import http
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import json


def home_view(request):
    especialidades = Especialidade.objects.all()
    
    context = {
        'especialidades':especialidades
    }
    
    return render(request, 'core/index.html', context)

from django.http import JsonResponse
from usuarios.models import Profissional  

from usuarios.forms import AvaliacaoForm  # Certifique-se de que o caminho para importar o AvaliacaoForm está correto

from django.contrib.contenttypes.models import ContentType

def calcular_media(objeto, Modelo):
    media = Avaliacao.objects.filter(
        content_type=ContentType.objects.get_for_model(Modelo), 
        object_id=objeto.id
    ).aggregate(Avg('rating'))
    return media['rating__avg']

# Função para calcular o total de avaliações
def total_avaliacoes(objeto, Modelo):
    return Avaliacao.objects.filter(
        content_type=ContentType.objects.get_for_model(Modelo),
        object_id=objeto.id
    ).count()
def calculate_stars(media):
    # Se a média for None, retornamos uma lista de estrelas vazias
    if media is None:
        return ["empty"] * 5
    
    # Calculamos o número de estrelas completas
    full_stars = int(media)
    
    # Verificamos se há necessidade de uma meia estrela
    half_star = 0 if media == full_stars else 1
    
    # Calculamos o número de estrelas vazias
    empty_stars = 5 - full_stars - half_star
    
    # Criamos e retornamos a lista final de estrelas
    return ["full"] * full_stars + ["half"] * half_star + ["empty"] * empty_stars
def perfil_profissional(request, profissional_id):
    profissional = get_object_or_404(Profissional, id=profissional_id)
    
    # Já estamos calculando esses valores aqui, então não precisamos repetir isso depois
    media = calcular_media(profissional, Profissional)
    stars = calculate_stars(media)
    total_av = total_avaliacoes(profissional, Profissional)

    avaliacoes = Avaliacao.objects.filter(
        content_type=ContentType.objects.get_for_model(profissional),
        object_id=profissional.id
    )
    
    is_cliente = hasattr(request.user, 'cliente')
    
    if request.method == 'POST':
        form = AvaliacaoForm(request.POST)
        
        if form.is_valid():
            avaliacao = form.save(commit=False)
            avaliacao.cliente = request.user.cliente  # Assumindo que o cliente é o usuário logado
            avaliacao.content_type = ContentType.objects.get_for_model(profissional)
            avaliacao.object_id = profissional.id
            avaliacao.save()
            
            # Recalcular a média após nova avaliação
            media = calcular_media(profissional)
            total_av += 1  # Atualizar o número total de avaliações
        else:
            print(form.errors)  # Debug: Imprimir os erros do formulário
    else:
        form = AvaliacaoForm()

    context = {
        'profissional': profissional,
        'form': form,
        'is_cliente': is_cliente,  
        'media': media,
        'total_avaliacoes': total_av,  # Aqui usamos total_av
        'avaliacoes': avaliacoes,
        'stars': stars
    }

    return render(request, 'core/perfil_profissional.html', context)

def perfil_clinica(request, clinica_id):
    clinica = get_object_or_404(Clinica, id=clinica_id)
    has_emergency = clinica.tipo_clinica.filter(nome__icontains='Emergência').exists()
    is_cliente = isinstance(request.user, Cliente)
    
    # Calculando valores aqui para evitar redundância
    media = calcular_media(clinica, Clinica)
    stars = calculate_stars(media)
    total_av = total_avaliacoes(clinica, Clinica)  # Renomeado para evitar conflito com a função
    
    if request.method == 'POST':
        form = AvaliacaoForm(request.POST)
        
        if form.is_valid():
            avaliacao = form.save(commit=False)
            avaliacao.cliente = request.user  # Asumindo que o cliente é o usuário logado
            avaliacao.content_type = ContentType.objects.get_for_model(clinica)
            avaliacao.object_id = clinica.id
            avaliacao.save()
            
            # Recalcular a média e total de avaliações após nova avaliação
            media = calcular_media(clinica)
            total_av += 1  # Atualizar o número total de avaliações
            
            # Aqui você pode adicionar algum redirecionamento ou mensagem de sucesso
            
    else:
        form = AvaliacaoForm()

    context = {
        'clinica': clinica,
        'form': form,
        'is_cliente': is_cliente,
        'has_emergency': has_emergency,
        'media': media,
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
            
    return JsonResponse({'estados': list(estados_ativos)})




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

        return JsonResponse({'cities': list(cities)})
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

def listar_profissionais(request):
    # Inicializa a query com a condição de que os profissionais sejam ativos e verificados por email
    q_objects = Q(is_active=True, email_verified=True)
    
    # Obtém os parâmetros da URL
    especialidade = request.GET.get('especialidade', None)
    estado = request.GET.get('estado', None)
    tipo_profissional = request.GET.get('tipo_profissional', None)
    bairros = request.GET.getlist('bairro', None)  # Obtém uma lista de bairros
    cidade = request.GET.get('cidade', None)
    convenios = request.GET.get('convenios', None)

    # Adiciona filtros à query com base nos parâmetros recebidos
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

    # Filtra apenas profissionais ativos
    queryset = Profissional.objects.filter(q_objects)

    # Paginação
    paginator = Paginator(queryset, 10)  # Mostra 2 profissionais por página
    page = request.GET.get('page')
    context = {}

    try:
        profissionais = paginator.page(page)
        enderecos = []
        
        for profissional in profissionais:
            enderecos.extend(list(profissional.enderecos.all().values('latitude', 'longitude')))
        
        context = {
            'profissionais': profissionais,
            'enderecos_json': json.dumps(enderecos)
        }

    except PageNotAnInteger:
        # Se a página não for um inteiro, entrega a primeira página
        profissionais = paginator.page(1)
        context['profissionais'] = profissionais

    except EmptyPage:
        # Se a página estiver fora do alcance, entrega a última página de resultados
        profissionais = paginator.page(paginator.num_pages)
        context['profissionais'] = profissionais

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
        
    # Filtra apenas profissionais ativos
    queryset = Clinica.objects.filter(q_objects)

    # Anotações adicionais (aqui você já pode usar 'queryset' porque ele já foi inicializado)
    has_emergency_subquery = Clinica.tipo_clinica.through.objects.filter(clinica_id=OuterRef('id'), tipoclinica__nome__icontains='Emergência')
    queryset = queryset.annotate(has_emergency=Exists(has_emergency_subquery))
    
    paginator = Paginator(queryset, 10)  # Mostra 10 clínicas por página
    
    page = request.GET.get('page')
    try:
        clinicas = paginator.page(page)
    except PageNotAnInteger:
        # Se a página não for um inteiro, entrega a primeira página
        clinicas = paginator.page(1)
    except EmptyPage:
        # Se a página estiver fora do alcance, entrega a última página de resultados
        clinicas = paginator.page(paginator.num_pages)
        
    context = {
            'clinicas': clinicas,
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
import requests
from django.shortcuts import render
from django.http import JsonResponse
from usuarios.models import Estado, Cidade, Especialidade
from django.db.models import Q
import http



def home_view(request):
    especialidades = Especialidade.objects.all()
    
    context = {
        'especialidades':especialidades
    }
    
    return render(request, 'core/index.html', context)

from django.http import JsonResponse
from usuarios.models import Profissional  

def buscar_estados(request):
    query = request.GET.get('query', '')
    especialidade = request.GET.get('especialidade', None)

    q_objects = Q(is_active=True) & Q(email_verified=True)

    if especialidade:
        q_objects &= Q(especialidades__nome__icontains=especialidade)
    
    profissionais_ativos = Profissional.objects.filter(q_objects).select_related('estado')
    estados_ativos = set([prof.estado.nome for prof in profissionais_ativos if prof.estado])

    estados_filtrados = [estado for estado in estados_ativos if query.lower() in estado.lower()][:5]
    
    return JsonResponse({'estados': estados_filtrados})


from django.shortcuts import render

def listar_profissionais(request):
    especialidade = request.GET.get('especialidade', None)
    estado = request.GET.get('estado', None)
    tipo_profissional = request.GET.get('tipo_profissional', None)

    # Filtra apenas profissionais ativos
    queryset = Profissional.objects.filter(is_active=True, email_verified=True)
    
    if especialidade:
        queryset = queryset.filter(especialidades__nome__icontains=especialidade)
        
    if estado:
        queryset = queryset.filter(estado__nome__icontains=estado)
        
    if tipo_profissional:
        queryset = queryset.filter(tipo_profissional=tipo_profissional)
    
    context = {
        'profissionais': queryset,
    }
    
    return render(request, 'core/listar_profissionais.html', context)

def get_especialidades(request):
    query = request.GET.get('query', '')
    estado = request.GET.get('estado', None)

    q_objects = Q(is_active=True) & Q(email_verified=True)

    if estado:
        q_objects &= Q(estado__nome__icontains=estado)

    profissionais_ativos = Profissional.objects.filter(q_objects).prefetch_related('especialidades')
    especialidades_ativas = set()
    for profissional in profissionais_ativos:
        for especialidade in profissional.especialidades.all():
            especialidades_ativas.add(especialidade.nome)
    
    especialidades_filtradas = [especialidade for especialidade in especialidades_ativas if query.lower() in especialidade.lower()][:5]

    return JsonResponse({'especialidades': especialidades_filtradas})



def get_states(request):
    states = Estado.objects.all().values_list('nome', flat=True)
    return JsonResponse({'states': list(states)})

def get_cities(request):
    state_name = request.GET.get('state', None)
    print(f"State Name: {state_name}")
    if state_name:
        estado = Estado.objects.get(nome=state_name)
        cities = estado.cidades.all().values_list('nome', flat=True)
        return JsonResponse({'cities': list(cities)})
    else:
        return JsonResponse({'cities': []})
    
def buscar_nomes(request):
    query = request.GET.get('query', '')
    
    q_objects = Q(is_active=True) & Q(email_verified=True)
    
    profissionais_ativos = Profissional.objects.filter(q_objects)
    nomes_ativos = set([prof.nome for prof in profissionais_ativos if prof.nome])

    nomes_filtrados = [nome for nome in nomes_ativos if query.lower() in nome.lower()][:5]
    
    return JsonResponse({'nomes': nomes_filtrados})

def buscar_tipos(request):
    query = request.GET.get('query', '')
    
    q_objects = Q(is_active=True) & Q(email_verified=True)
    
    profissionais_ativos = Profissional.objects.filter(q_objects)
    tipos_ativos = set([prof.tipo_profissional for prof in profissionais_ativos if prof.tipo_profissional])

    tipos_filtrados = [tipo for tipo in tipos_ativos if query.lower() in tipo.lower()][:5]
    
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
from django.core.management.base import BaseCommand
import requests
from usuarios.models import Estado, Cidade, Distrito  

class Command(BaseCommand):
    help = 'Popula o banco de dados com estados e cidades do Brasil'

    def handle(self, *args, **kwargs):
        self.stdout.write('Iniciando a população do banco de dados...')

        # Sua lógica aqui
        self.populate_db()
        
        self.stdout.write('Banco de dados populado com sucesso!')

    def populate_db(self):
        # Puxando estados
        response_estados = requests.get("https://servicodados.ibge.gov.br/api/v1/localidades/estados")
        estados = response_estados.json()

        for estado in estados:
            estado_obj, created = Estado.objects.get_or_create(nome=estado['nome'])
            
            # Puxando cidades para o estado atual
            response_cidades = requests.get(f"https://servicodados.ibge.gov.br/api/v1/localidades/estados/{estado['id']}/municipios")
            cidades = response_cidades.json()
            
            for cidade in cidades:
                cidade_obj, created = Cidade.objects.get_or_create(nome=cidade['nome'], estado=estado_obj)
                
                # Puxando distritos para a cidade atual
                response_distritos = requests.get(f"https://servicodados.ibge.gov.br/api/v1/localidades/municipios/{cidade['id']}/distritos")
                distritos = response_distritos.json()
                
                for distrito in distritos:
                    # Substitua essa parte pelo seu modelo e lógica para salvar distritos
                    Distrito.objects.get_or_create(nome=distrito['nome'], cidade=cidade_obj)


from django.core.management.base import BaseCommand
from usuarios.models import TipoClinica, TipoProfissional

class Command(BaseCommand):
    help = 'Popula o banco de dados com tipos básicos de clínica e profissionais'

    def handle(self, *args, **options):
        # Criar tipos de clínica
        tipos_clinica = [
            'Exames e Laboratórios',
            'Hospital',
            'Clínica Médica',
            'Consultório',
        ]
        
        for tipo_nome in tipos_clinica:
            tipo_clinica, created = TipoClinica.objects.get_or_create(nome=tipo_nome)
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Tipo de clínica "{tipo_nome}" criado com sucesso')
                )
            else:
                self.stdout.write(f'Tipo de clínica "{tipo_nome}" já existe')

        # Criar tipos de profissional
        tipos_profissional = [
            'Médico',
            'Dentista',
            'Fisioterapeuta',
            'Psicólogo',
            'Nutricionista',
        ]
        
        for tipo_nome in tipos_profissional:
            tipo_profissional, created = TipoProfissional.objects.get_or_create(nome=tipo_nome)
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Tipo de profissional "{tipo_nome}" criado com sucesso')
                )
            else:
                self.stdout.write(f'Tipo de profissional "{tipo_nome}" já existe')

        self.stdout.write(
            self.style.SUCCESS('Comando executado com sucesso!')
        )

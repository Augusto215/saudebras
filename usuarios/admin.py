from django.contrib import admin
from .models import *




class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nome', 'sobrenome', 'email', 'cidade', 'bairro')
    search_fields = ('username', 'email')

# Profissional Admin
class ProfissionalAdmin(admin.ModelAdmin):
    list_display = ('nome','sobrenome','tipo_profissional', 'Especialidades', 'email', 'is_active' )

    def Especialidades(self, obj):
        return ', '.join([str(especialidade) for especialidade in obj.especialidades.all()])
    
   

class ClinicaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'display_tipo_clinica', 'display_tipo_profissional', 'display_estados', 'is_active', 'display_convenios')
    
    def display_tipo_clinica(self, obj):
        return ", ".join([tipo_clinica.nome for tipo_clinica in obj.tipo_clinica.all()])
    display_tipo_clinica.short_description = "Tipos de Clínica"
    
    def display_tipo_profissional(self, obj):
        return ", ".join([tipo_profissional.nome for tipo_profissional in obj.tipo_profissional.all()])
    display_tipo_profissional.short_description = "Tipos de Profissional"
    
    def display_estados(self, obj):
        return ", ".join([estados.nome for estados in obj.estados.all()])
    display_estados.short_description = "Estados"

    
    def display_convenios(self, obj):
        return ", ".join([convenios.nome for convenios in obj.convenios.all()])
    display_convenios.short_description = "Convenio"
    
    
# Registra o modelo Especialidade para que ele apareça no painel admin
admin.site.register(Cliente, ClienteAdmin)
admin.site.register(Profissional, ProfissionalAdmin)
admin.site.register(Clinica, ClinicaAdmin)
admin.site.register(Especialidade)
admin.site.register(Convenio)
admin.site.register(Idioma)
admin.site.register(Servico)
admin.site.register(Foto)
admin.site.register(CEP)
admin.site.register(PerguntaResposta)
admin.site.register(Subscription)
admin.site.register(TipoProfissional)
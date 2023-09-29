from django.contrib import admin
from .models import Estado, Cidade, Bairro, Cliente, Profissional, CustomUser, Especialidade




class ClienteAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'cidade', 'bairro')
    search_fields = ('username', 'email')

# Profissional Admin
class ProfissionalAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'mostrar_especialidades')

    def mostrar_especialidades(self, obj):
        return ', '.join([str(especialidade) for especialidade in obj.especialidades.all()])



# Registra o modelo Especialidade para que ele apareça no painel admin
admin.site.register(Especialidade)
admin.site.register(Cliente, ClienteAdmin)
admin.site.register(Profissional, ProfissionalAdmin)

from django.contrib import admin
from .models import ContatoMensagem

# Register your models here.

@admin.register(ContatoMensagem)
class ContatoMensagemAdmin(admin.ModelAdmin):
    list_display = ('nome', 'email', 'assunto', 'status', 'data_criacao')
    list_filter = ('assunto', 'status', 'data_criacao')
    search_fields = ('nome', 'email', 'mensagem')
    readonly_fields = ('data_criacao',)
    list_editable = ('status',)
    ordering = ('-data_criacao',)
    
    fieldsets = (
        ('Informações do Contato', {
            'fields': ('nome', 'email', 'telefone', 'assunto')
        }),
        ('Mensagem', {
            'fields': ('mensagem',)
        }),
        ('Status e Datas', {
            'fields': ('status', 'data_criacao', 'data_resposta')
        }),
        ('Resposta', {
            'fields': ('resposta',),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if change and 'status' in form.changed_data and obj.status == 'respondido':
            if not obj.data_resposta:
                from django.utils import timezone
                obj.data_resposta = timezone.now()
        super().save_model(request, obj, form, change)

from django.db import models
from django.utils import timezone

# Create your models here.

class ContatoMensagem(models.Model):
    ASSUNTO_CHOICES = [
        ('duvidas', 'Dúvidas Gerais'),
        ('agendamento', 'Agendamento de Consulta'),
        ('suporte', 'Suporte Técnico'),
        ('reclamacao', 'Reclamação'),
        ('sugestao', 'Sugestão'),
        ('parceria', 'Parceria'),
        ('outros', 'Outros'),
    ]
    
    STATUS_CHOICES = [
        ('novo', 'Novo'),
        ('em_andamento', 'Em Andamento'),
        ('respondido', 'Respondido'),
        ('resolvido', 'Resolvido'),
    ]
    
    nome = models.CharField(max_length=100, verbose_name='Nome Completo')
    email = models.EmailField(verbose_name='Email')
    telefone = models.CharField(max_length=20, verbose_name='Telefone')
    assunto = models.CharField(max_length=20, choices=ASSUNTO_CHOICES, verbose_name='Assunto')
    mensagem = models.TextField(verbose_name='Mensagem')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='novo', verbose_name='Status')
    data_criacao = models.DateTimeField(default=timezone.now, verbose_name='Data de Criação')
    data_resposta = models.DateTimeField(null=True, blank=True, verbose_name='Data de Resposta')
    resposta = models.TextField(blank=True, verbose_name='Resposta')
    
    class Meta:
        verbose_name = 'Mensagem de Contato'
        verbose_name_plural = 'Mensagens de Contato'
        ordering = ['-data_criacao']
    
    def __str__(self):
        return f'{self.nome} - {self.get_assunto_display()} - {self.data_criacao.strftime("%d/%m/%Y")}'
    
    @property
    def tempo_resposta(self):
        if self.data_resposta:
            return self.data_resposta - self.data_criacao
        return None
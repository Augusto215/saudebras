# Generated by Django 4.2.5 on 2023-10-23 01:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0013_perguntaresposta_cliente'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='perguntaresposta',
            name='object_id',
        ),
        migrations.AddField(
            model_name='profissional',
            name='perguntas',
            field=models.ManyToManyField(blank=True, related_name='profissionais', to='usuarios.perguntaresposta'),
        ),
    ]
# Generated by Django 4.2.5 on 2023-10-10 02:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profissional',
            name='tipo_profissional',
        ),
        migrations.AddField(
            model_name='profissional',
            name='tipo_profissional',
            field=models.CharField(blank=True, choices=[('Médico', 'Médico'), ('Dentista', 'Dentista')], max_length=50),
        ),
    ]

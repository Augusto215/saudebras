# Generated by Django 4.2.5 on 2023-10-15 03:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0006_endereco_clinica_endereco_profissional'),
    ]

    operations = [
        migrations.AddField(
            model_name='cliente',
            name='foto',
            field=models.ImageField(blank=True, default='/images/unknown.png', null=True, upload_to='images/'),
        ),
    ]
# Generated by Django 4.2.5 on 2023-10-15 17:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0007_cliente_foto'),
    ]

    operations = [
        migrations.AddField(
            model_name='cliente',
            name='cep',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
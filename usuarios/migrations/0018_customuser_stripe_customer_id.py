# Generated by Django 4.2.5 on 2023-10-24 13:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0017_clinica_perguntas'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='stripe_customer_id',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]

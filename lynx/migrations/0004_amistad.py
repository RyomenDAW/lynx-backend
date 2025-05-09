# Generated by Django 5.1.1 on 2025-04-29 12:21

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lynx', '0003_codigopromocional_usado'),
    ]

    operations = [
        migrations.CreateModel(
            name='Amistad',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('aceptada', models.BooleanField(default=False)),
                ('fecha', models.DateTimeField(auto_now_add=True)),
                ('receptor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='amistades_recibidas', to=settings.AUTH_USER_MODEL)),
                ('solicitante', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='amistades_enviadas', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('solicitante', 'receptor')},
            },
        ),
    ]

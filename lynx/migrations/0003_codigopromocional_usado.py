# Generated by Django 5.1.1 on 2025-04-22 17:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lynx', '0002_remove_codigopromocional_item_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='codigopromocional',
            name='usado',
            field=models.BooleanField(default=False),
        ),
    ]

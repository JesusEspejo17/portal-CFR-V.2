# Generated by Django 5.1.2 on 2025-01-15 16:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('erp', '0008_alter_orden_compra_systemdate'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='orden_compra',
            name='Orden',
        ),
    ]
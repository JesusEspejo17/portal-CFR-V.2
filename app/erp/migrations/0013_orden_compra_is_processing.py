# Generated by Django 5.1.2 on 2025-01-20 17:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('erp', '0012_remove_orden_compra_docnumsap_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='orden_compra',
            name='is_processing',
            field=models.BooleanField(default=False, verbose_name='En proceso'),
        ),
    ]

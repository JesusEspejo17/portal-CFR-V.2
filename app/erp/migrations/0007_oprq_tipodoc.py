# Generated by Django 5.1.2 on 2025-01-14 15:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('erp', '0006_orden_compra'),
    ]

    operations = [
        migrations.AddField(
            model_name='oprq',
            name='TipoDoc',
            field=models.CharField(default='SOL', max_length=10, verbose_name='TipoDocumentos'),
        ),
    ]

# Generated by Django 5.1.2 on 2025-01-22 17:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('erp', '0015_occ_ocd1'),
    ]

    operations = [
        migrations.AddField(
            model_name='prq1',
            name='LineCount',
            field=models.IntegerField(default=0),
        ),
    ]

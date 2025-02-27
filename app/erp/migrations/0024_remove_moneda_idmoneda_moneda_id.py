from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('erp', '0023_prq1_totalimpdet'),  # Asegúrate de que esto apunte a la última migración exitosa
    ]

    operations = [
        migrations.RemoveField(
            model_name='moneda',
            name='idMoneda',
        ),
        migrations.AddField(
            model_name='moneda',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]
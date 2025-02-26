from rest_framework import serializers
from erp.models import Moneda

class MonedaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Moneda
        fields = '__all__'  # O especifica los campos que deseas exponer

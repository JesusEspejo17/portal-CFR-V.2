from rest_framework import viewsets
from erp.models import Moneda
from .serializers import MonedaSerializer

class MonedaViewSet(viewsets.ModelViewSet):
    queryset = Moneda.objects.all()
    serializer_class = MonedaSerializer

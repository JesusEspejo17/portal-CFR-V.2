from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MonedaViewSet

app_name = 'api'  # Define el namespace de la API

router = DefaultRouter()
router.register(r'monedas', MonedaViewSet)

urlpatterns = [
    path('', include(router.urls)),  # Incluir todas las rutas generadas automáticamente
]

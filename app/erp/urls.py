from django.urls import path
from erp.views import *

urlpatterns = [
    path('solicitud_compra/', solicitudcompra, name='solicitudcompra'),
    path('listar_prod/',listado_articulos, name="listar_prod"),
    path('listar_serv/',listado_servicios, name="listar_serv"),
    path('obtener_nombre_serie/', obtener_nombre_serie, name="obtener_nombre_serie"),
    path('obtener_impuesto/', obtener_impuesto, name="obtener_impuesto"),
    path('obtener_numero_serie/', obtener_numero_serie, name="obtener_numero_serie"),
    path('procesar_solicitud/', ListSolicitudesCompra.as_view(), name="listar_solicitudes"),
    path('solicitud/aprobar/<int:id>',solicitudAprobar, name="aprobar_solicitud"),
    path('solicitud/rechazar/<int:id>',solicitudRechazar, name="rechazar_solicitud"),
    path('solicitud/contabilizar/<int:id>',solicitudContabilizar, name="contabilizar_solicitud"),
    path('export_data_as_json/', export_data_as_json, name="export_data_as_json"),
    path('aprobar_masivo/', solicitudAprobarMasivo, name="aprobar_masivo"),
    path('rechazar_masivo/', solicitudRechazarMasivo, name="rechazar_masivo"),
    path('contabilizar_masivo/', solicitudContabilizarMasivo, name="contabilizar_masivo"),
    path('getUserGroups/', get_user_groups, name='get_user_groups'),
    path('procesar_logistica/',ListLogistica.as_view(), name="listar_logistica")
]

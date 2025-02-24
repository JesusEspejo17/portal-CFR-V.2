from django.urls import path
from erp.views import *
import erp.views as views

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
    path('procesar_logistica/',ListLogistica.as_view(), name="listar_logistica"),
    path('logistica/guardarProducto/', export_data_as_jsonProductos, name='guardar_producto'),
    path('logistica/guardarServicio/', export_data_as_jsonServicios, name='guardar_servicio'),
    path('listar_orden/',OrdenCompraListView.as_view(), name="listar_ordenes"),
    path('solicitud/detalle/<str:base_entry>/', views.get_solicitud_detalle, name='get_solicitud_detalle'),
    path('solicitud/detalle_producto/<int:doc_num>/', views.get_solicitud_detalle_producto, name='get_solicitud_detalle_producto'),
    path('solicitud/detalle_servicio/<int:doc_num>/', views.get_solicitud_detalle_servicio, name='get_solicitud_detalle_servicio'),
    path('getLineDetails/', views.get_line_details, name='get_line_details'),
    path('contabilizadas/', ListContabilizadas.as_view(), name='listar_contabilizadas'),
]

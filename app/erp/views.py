from typing import Any
import json
import requests
from django.http import HttpRequest
from django.http.response import HttpResponse as HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required, permission_required
from erp.models import *
from user.models import User
from erp.forms import *
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView, ListView
from datetime import date, datetime
from django.http import JsonResponse
from django.db import transaction
from app.mixins import ValidatePermissionRequiredMixin,ValidatePermissionRequiredMixin2
from user.tests import send_email_to_validator, send_email_to_user
from django.contrib.auth.models import Group, Permission
from django.utils import timezone
import time
from django.db.models import Prefetch, Q
import traceback
import logging  # Añadir al inicio del archivo
logger = logging.getLogger(__name__)


def listado_servicios(request):
    template_name="Servicio/buscar_servicio.html"
    if request.method=='GET':
        Servicio = OITM.objects.filter(TypeProduct__icontains='S')
        cuentaContable_serv=OACT.objects.filter()
        cuenta_contable_json = json.dumps(list(cuentaContable_serv.values('AcctCode', 'AcctName')))
        socioNegocio_serv=OCRD.objects.filter()
        socioNegocio_json = json.dumps(list(socioNegocio_serv.values('CardCode', 'CardName')))
        
        dimension=Dimensiones.objects.filter()
        dimension_json = json.dumps(list(dimension.values('nombre', 'descripcion')))
        context={'Servicio':Servicio,
                  'cuentaContable_serv':cuentaContable_serv,
                  'socioNegocio_serv':socioNegocio_serv,
                  'Dimension':dimension,
                  'cuenta_contable_json': cuenta_contable_json,
                  'socioNegocio_json': socioNegocio_json,
                  'dimension_json': dimension_json}
    return render(request, template_name, context)
    
def listado_articulos(request):
    template_name="Articulo/buscar_articulo.html"
    if request.method=='GET':
        Articulo = OITM.objects.filter(TypeProduct__icontains='P')
        almacen=OWHS.objects.exclude(WhsName__icontains='Sin Almacen')
        almacenes_json = json.dumps(list(almacen.values('WhsCode', 'WhsName')))
        unidadMedida=OUOM.objects.exclude(Name__icontains='Sin Unidad')
        medida_json = json.dumps(list(unidadMedida.values('Code', 'Name')))
        socioNegocio=OCRD.objects.filter()
        socioNegocio_json = json.dumps(list(socioNegocio.values('CardCode', 'CardName')))
        dimension=Dimensiones.objects.filter()
        dimension_json = json.dumps(list(dimension.values('nombre', 'descripcion')))
        contexto={'Articulo':Articulo,
                  'almacen':almacen,
                  'unidadMedida':unidadMedida,
                  'socioNegocio':socioNegocio,
                  'Dimension':dimension,
                  'dimension_json':dimension_json,
                  'almacenes_json':almacenes_json,
                  'medida_json': medida_json,
                  'proveedor_json':socioNegocio_json}
    return render(request, template_name, contexto)


@login_required(login_url='/login/')
@permission_required(['erp.add_oprq', 'erp.view_oprq', 'erp.view_oprq'], login_url='bases:sin_privilegios')
# def solicitudcompra(request):
#     template_name = 'SolicitudCompra/create_solicitud_compra.html'
#     fecha = datetime.today().strftime('%d-%m-%Y')
#     success_url = reverse_lazy('erp:listar_solicitudes')
#     if request.method == 'GET':
#         coin = Moneda.objects.filter()
#         impuestos = OSTA.objects.filter()
#         departamento = Departamento.objects.filter()
#         serie = Series.objects.filter()

#         cuentaContable = OACT.objects.exclude(AcctName__icontains='Sin Cuenta Contable')
#         cuentaContable_json = json.dumps(list(cuentaContable.values('AcctCode', 'AcctName')))

#         socioNegocio = OCRD.objects.filter()
#         socioNegocio_json = json.dumps(list(socioNegocio.values('CardCode', 'CardName')))

#         medida = OUOM.objects.exclude(Name__icontains='Sin Unidad')
#         medida_json = json.dumps(list(medida.values('Code', 'Name')))

#         almacen = OWHS.objects.exclude(WhsName__icontains='Sin Almacen')
#         almacenes_json = json.dumps(list(almacen.values('WhsCode', 'WhsName')))

#         dimension = Dimensiones.objects.filter()
#         dimension_json = json.dumps(list(dimension.values('nombre', 'descripcion')))

#         grupo_especifico = Group.objects.get(name='Administrador')
#         pertenece_al_grupo = request.user.groups.filter(name=grupo_especifico).exists()
#         contexto = {
#             'moneda': coin,
#             'OSTA': impuestos,
#             'title': ' Nueva Solicitud de Compra',
#             'fecha': fecha,
#             'serie': serie,
#             'Departamento': departamento,
#             'cuenta_contable': cuentaContable_json,
#             'socio_negocio': socioNegocio_json,
#             'almacen': almacenes_json,
#             'medida': medida_json,
#             'dimension': dimension_json
#         }
#         return render(request, template_name, contexto)
#     if request.method == 'POST':
#         try:
#             with transaction.atomic():
#                 print("Iniciando creación de solicitud...")
#                 NombreSerie = request.POST.get('serie')
#                 serie = Series.objects.get(Nombre=NombreSerie)
#                 print(f"Serie encontrada: {NombreSerie}")
#                 if (serie.NumeroSiguiente > serie.UltimoNumero):
#                     msg = "ERROR: Se ha llegado al límite de solicitudes de compra guardadas por el sistema para esa serie."
#                     render(request, template_name, {'error message': msg})

#                 # Cargamos vents para los productos
#                 vents_data = request.POST.get('vents_data', '{}')
#                 servs_data = request.POST.get('servs_data', '{}')
#                 print(f"Datos recibidos - Productos: {vents_data}")
#                 print(f"Datos recibidos - Servicios: {servs_data}")

#                 # Procesa los datos JSON de vents_data y servs_data como necesites
#                 vents = json.loads(vents_data)
#                 servs = json.loads(servs_data)

#                 if not vents and not servs:
#                     msg = "ERROR: No se ha ingresado ningún producto o servicio."
#                     print("Error: No hay productos ni servicios")
#                     return render(request, template_name, {'error_message': msg})

#                 # Inicialización de datos necesarios
#                 print("Creando encabezado OPRQ...")
#                 encabezado = OPRQ()
#                 # User
#                 nameUser = request.POST.get('idUser')
#                 usuario = User.objects.get(id=nameUser)

#                 # Impuestos
#                 imp = request.POST.get('TaxCode')
#                 cadImpuesto = imp.split('-', 1)  # imp está en el formato "Nombre - Codigo"
#                 code_Impuesto = cadImpuesto[-1].strip()
#                 impuesto = OSTA.objects.get(Code=code_Impuesto)

#                 # Moneda
#                 abreviacionMoneda = request.POST.get('moneda')
#                 moneda = Moneda.objects.get(MonedaAbrev=abreviacionMoneda)

#                 # Departamento
#                 deptName = request.POST.get('Department')
#                 departamento = Departamento.objects.get(Name=deptName)

#                 # Save encabezado
#                 encabezado.DocNum = request.POST.get('DocNum')
#                 encabezado.ReqIdUser = usuario
#                 encabezado.ReqCode = usuario.SAP_Code
#                 encabezado.ReqType = usuario.UserType
#                 encabezado.Department = departamento
#                 encabezado.Serie = serie.CodigoSerie
#                 encabezado.DocStatus = "P"  # P: pendiente, A: aprobado, R: rechazado C:contabilizado
#                 # Si el arreglo de servicios está vacío, se está agregando un producto
#                 if (servs == [] and len(vents) > 0):
#                     encabezado.DocType = "I"
#                 # Si el arreglo de productos está vacío, se está agregando un servicio
#                 elif (vents == [] and len(servs) > 0):
#                     encabezado.DocType = "S"
#                 doc_date_str = request.POST.get('DocDate')
#                 doc_date = datetime.strptime(doc_date_str, '%d-%m-%Y').strftime('%Y-%m-%d')
#                 encabezado.DocDate = doc_date
#                 doc_due_date_str = request.POST.get('DocDueDate')
#                 doc_due_date = datetime.strptime(doc_due_date_str, '%d-%m-%Y').strftime('%Y-%m-%d')
#                 encabezado.DocDueDate = doc_due_date
#                 doc_system_date_str = request.POST.get('SystemDate')
#                 doc_system_date = datetime.strptime(doc_system_date_str, '%d-%m-%Y').strftime('%Y-%m-%d')
#                 encabezado.SystemDate = doc_system_date
#                 doc_req_date_str = request.POST.get('ReqDate')
#                 doc_req_date = datetime.strptime(doc_req_date_str, '%d-%m-%Y').strftime('%Y-%m-%d')
#                 encabezado.ReqDate = doc_req_date
#                 encabezado.TaxCode = impuesto
#                 encabezado.moneda = moneda
#                 encabezado.Comments = request.POST.get('Comments')
#                 encabezado.Total = float(request.POST.get('Total'))
#                 encabezado.TotalImp = float(request.POST.get('TotalImp'))
#                 encabezado.save()
#                 print(f"Encabezado creado con ID: {encabezado.pk}")

#                 # Calcular la tasa de impuesto
#                 tasa_impuesto = impuesto.Rate

#                 # Save detalle
#                 if servs == [] and len(vents) > 0:
#                     print("Procesando productos...")
#                     for i in vents:
#                         try:
#                             print(f"Creando detalle para producto: {i['code']}")
#                             detalle = PRQ1()
#                             item = OITM.objects.get(ItemCode=i['code'])
#                             proveedor = None
#                             if i['proveedor']:
#                                 proveedor = OCRD.objects.get(CardName=i['proveedor'])
#                             uni_med = OUOM.objects.get(Code=i['medida'])
#                             almacen = OWHS.objects.get(WhsName=i['almacen'])
#                             cuentaContable = OACT.objects.get(AcctName="Sin Cuenta Contable")
#                             dimension = Dimensiones.objects.get(descripcion=i['dimension'])
#                             detalle.NumDoc = encabezado
#                             detalle.ItemCode = item
#                             detalle.LineVendor = proveedor if proveedor else None
#                             detalle.Description = i['description']
#                             detalle.Quantity = i['cant']
#                             detalle.UnidadMedida = uni_med
#                             detalle.Currency = moneda
#                             detalle.Almacen = almacen
#                             detalle.CuentaMayor = cuentaContable
#                             detalle.total = i['precio_total']
#                             detalle.totalimpdet = float(i['precio_total']) * (1 + tasa_impuesto)  # Calcular total con impuesto
#                             if 'price' in i:
#                                 try:
#                                     detalle.Precio = float(i['price'])
#                                     print("Precio asignado:", detalle.Precio)
#                                 except ValueError:
#                                     detalle.Precio = 0.0
#                             else:
#                                 detalle.Precio = 0.0
#                                 print("Advertencia: 'precio' no encontrado en item:", i)
#                             detalle.idDimension = dimension
#                             detalle.save()
#                         except Exception as e:
#                             print(f"Error al guardar detalle de producto: {str(e)}")
#                             raise
#                 elif vents == [] and len(servs) > 0:
#                     print("Procesando servicios...")
#                     for i in servs:
#                         try:
#                             print(f"Creando detalle para servicio: {i['code']}")
#                             detalle = PRQ1()
#                             item = OITM.objects.get(ItemCode=i['code'])
#                             proveedor = None
#                             if i['proveedor']:
#                                 proveedor = OCRD.objects.get(CardName=i['proveedor'])
#                             cuentaContable = OACT.objects.get(AcctName=i['cuenta_contable'])
#                             uni_med = OUOM.objects.get(Code="Sin Unidad")
#                             almacen = OWHS.objects.get(WhsName="Sin Almacen")
#                             dimension = Dimensiones.objects.get(descripcion=i['dimension'])
#                             detalle.NumDoc = encabezado
#                             detalle.ItemCode = item
#                             detalle.LineVendor = proveedor if proveedor else None
#                             detalle.Description = i['description']
#                             detalle.Quantity = i['cant']
#                             detalle.UnidadMedida = uni_med
#                             detalle.Currency = moneda
#                             detalle.Almacen = almacen
#                             detalle.CuentaMayor = cuentaContable
#                             detalle.total = i['precio_total']
#                             detalle.totalimpdet = float(i['precio_total']) * (1 + tasa_impuesto)  # Calcular total con impuesto
#                             if 'price' in i:
#                                 try:
#                                     detalle.Precio = float(i['price'])
#                                     print("Precio asignado:", detalle.Precio)
#                                 except ValueError:
#                                     detalle.Precio = 0.0
#                             else:
#                                 detalle.Precio = 0.0
#                                 print("Advertencia: 'precio' no encontrado en item:", i)
#                             detalle.idDimension = dimension
#                             detalle.save()
#                             print(f"Detalle de servicio guardado con ID: {detalle.pk}")
#                         except Exception as e:
#                             print(f"Error al guardar detalle de servicio: {str(e)}")
#                             raise

#                 # Actualizar modelo Series
#                 if serie:
#                     serie.NumeroSiguiente += 1
#                     serie.save()
#                     print(f"Serie actualizada: {serie.NumeroSiguiente}")
#                 success_message = "La solicitud de compra se ha guardado correctamente."
#                 print("Solicitud creada exitosamente")
#                 send_email_to_validator()
#                 return render(request, template_name, {'success_message': "La solicitud de compra se ha guardado correctamente."})

#         except Exception as e:
#             print(f"Error general: {str(e)}")
#             print(f"Tipo de error: {type(e)}")
#             print(f"Traceback completo: {traceback.format_exc()}")
#             msg = f"Error al insertar datos maestros: {str(e)}"  # Corregido
#             return render(request, template_name, {'error_message': msg})
#             # Considera registrar el error en un archivo de log
#             render(request, template_name, {'error_message': msg})
#         return redirect(success_url)

def solicitudcompra(request):
    template_name = 'SolicitudCompra/create_solicitud_compra.html'
    fecha = datetime.today().strftime('%d-%m-%Y')
    success_url = reverse_lazy('erp:listar_solicitudes')
    if request.method == 'GET':
        coin = Moneda.objects.filter()
        impuestos = OSTA.objects.filter()
        departamento = Departamento.objects.filter()
        serie = Series.objects.filter()

        cuentaContable = OACT.objects.exclude(AcctName__icontains='Sin Cuenta Contable')
        cuentaContable_json = json.dumps(list(cuentaContable.values('AcctCode', 'AcctName')))

        socioNegocio = OCRD.objects.filter()
        socioNegocio_json = json.dumps(list(socioNegocio.values('CardCode', 'CardName')))

        medida = OUOM.objects.exclude(Name__icontains='Sin Unidad')
        medida_json = json.dumps(list(medida.values('Code', 'Name')))

        almacen = OWHS.objects.exclude(WhsName__icontains='Sin Almacen')
        almacenes_json = json.dumps(list(almacen.values('WhsCode', 'WhsName')))

        dimension = Dimensiones.objects.filter()
        dimension_json = json.dumps(list(dimension.values('nombre', 'descripcion')))

        grupo_especifico = Group.objects.get(name='Administrador')
        pertenece_al_grupo = request.user.groups.filter(name=grupo_especifico).exists()
        contexto = {
            'moneda': coin,
            'OSTA': impuestos,
            'title': ' Nueva Solicitud de Compra',
            'fecha': fecha,
            'serie': serie,
            'Departamento': departamento,
            'cuenta_contable': cuentaContable_json,
            'socio_negocio': socioNegocio_json,
            'almacen': almacenes_json,
            'medida': medida_json,
            'dimension': dimension_json
        }
        return render(request, template_name, contexto)
    if request.method == 'POST':
        try:
            with transaction.atomic():
                print("Iniciando creación de solicitud...")
                NombreSerie = request.POST.get('serie')
                serie = Series.objects.get(Nombre=NombreSerie)
                print(f"Serie encontrada: {NombreSerie}")
                if (serie.NumeroSiguiente > serie.UltimoNumero):
                    msg = "ERROR: Se ha llegado al límite de solicitudes de compra guardadas por el sistema para esa serie."
                    render(request, template_name, {'error message': msg})

                # Cargamos vents para los productos
                vents_data = request.POST.get('vents_data', '{}')
                servs_data = request.POST.get('servs_data', '{}')
                print(f"Datos recibidos - Productos: {vents_data}")
                print(f"Datos recibidos - Servicios: {servs_data}")

                # Procesa los datos JSON de vents_data y servs_data como necesites
                vents = json.loads(vents_data)
                servs = json.loads(servs_data)

                if not vents and not servs:
                    msg = "ERROR: No se ha ingresado ningún producto o servicio."
                    print("Error: No hay productos ni servicios")
                    return render(request, template_name, {'error_message': msg})

                # Inicialización de datos necesarios
                print("Creando encabezado OPRQ...")
                encabezado = OPRQ()
                # User
                nameUser = request.POST.get('idUser')
                usuario = User.objects.get(id=nameUser)

                # Impuestos
                imp = request.POST.get('TaxCode')
                cadImpuesto = imp.split('-', 1)  # imp está en el formato "Nombre - Codigo"
                code_Impuesto = cadImpuesto[-1].strip()
                impuesto = OSTA.objects.get(Code=code_Impuesto)

                # Moneda
                abreviacionMoneda = request.POST.get('moneda')
                today = timezone.now().date()
                moneda = Moneda.objects.filter(MonedaAbrev=abreviacionMoneda, TCDate=today).first()
                if not moneda:
                    raise ValueError("No se encontró una moneda para la fecha actual.")

                # Departamento
                deptName = request.POST.get('Department')
                departamento = Departamento.objects.get(Name=deptName)

                # Save encabezado
                encabezado.DocNum = request.POST.get('DocNum')
                encabezado.ReqIdUser = usuario
                encabezado.ReqCode = usuario.SAP_Code
                encabezado.ReqType = usuario.UserType
                encabezado.Department = departamento
                encabezado.Serie = serie.CodigoSerie
                encabezado.DocStatus = "P"  # P: pendiente, A: aprobado, R: rechazado C:contabilizado
                # Si el arreglo de servicios está vacío, se está agregando un producto
                if (servs == [] and len(vents) > 0):
                    encabezado.DocType = "I"
                # Si el arreglo de productos está vacío, se está agregando un servicio
                elif (vents == [] and len(servs) > 0):
                    encabezado.DocType = "S"
                doc_date_str = request.POST.get('DocDate')
                doc_date = datetime.strptime(doc_date_str, '%d-%m-%Y').strftime('%Y-%m-%d')
                encabezado.DocDate = doc_date
                doc_due_date_str = request.POST.get('DocDueDate')
                doc_due_date = datetime.strptime(doc_due_date_str, '%d-%m-%Y').strftime('%Y-%m-%d')
                encabezado.DocDueDate = doc_due_date
                doc_system_date_str = request.POST.get('SystemDate')
                doc_system_date = datetime.strptime(doc_system_date_str, '%d-%m-%Y').strftime('%Y-%m-%d')
                encabezado.SystemDate = doc_system_date
                doc_req_date_str = request.POST.get('ReqDate')
                doc_req_date = datetime.strptime(doc_req_date_str, '%d-%m-%Y').strftime('%Y-%m-%d')
                encabezado.ReqDate = doc_req_date
                encabezado.TaxCode = impuesto
                encabezado.moneda = moneda
                encabezado.Comments = request.POST.get('Comments')
                encabezado.Total = float(request.POST.get('Total'))
                encabezado.TotalImp = float(request.POST.get('TotalImp'))
                encabezado.save()
                print(f"Encabezado creado con ID: {encabezado.pk}")

                # Calcular la tasa de impuesto
                tasa_impuesto = impuesto.Rate

                # Save detalle
                if servs == [] and len(vents) > 0:
                    print("Procesando productos...")
                    for i in vents:
                        try:
                            print(f"Creando detalle para producto: {i['code']}")
                            detalle = PRQ1()
                            item = OITM.objects.get(ItemCode=i['code'])
                            proveedor = None
                            if i['proveedor']:
                                proveedor = OCRD.objects.get(CardName=i['proveedor'])
                            uni_med = OUOM.objects.get(Code=i['medida'])
                            almacen = OWHS.objects.get(WhsName=i['almacen'])
                            cuentaContable = OACT.objects.get(AcctName="Sin Cuenta Contable")
                            dimension = Dimensiones.objects.get(descripcion=i['dimension'])
                            detalle.NumDoc = encabezado
                            detalle.ItemCode = item
                            detalle.LineVendor = proveedor if proveedor else None
                            detalle.Description = i['description']
                            detalle.Quantity = i['cant']
                            detalle.UnidadMedida = uni_med
                            detalle.Currency = moneda
                            detalle.Almacen = almacen
                            detalle.CuentaMayor = cuentaContable
                            detalle.total = i['precio_total']
                            detalle.totalimpdet = float(i['precio_total']) * (1 + tasa_impuesto)  # Calcular total con impuesto
                            if 'price' in i:
                                try:
                                    detalle.Precio = float(i['price'])
                                    print("Precio asignado:", detalle.Precio)
                                except ValueError:
                                    detalle.Precio = 0.0
                            else:
                                detalle.Precio = 0.0
                                print("Advertencia: 'precio' no encontrado en item:", i)
                            detalle.idDimension = dimension
                            detalle.save()
                        except Exception as e:
                            print(f"Error al guardar detalle de producto: {str(e)}")
                            raise
                elif vents == [] and len(servs) > 0:
                    print("Procesando servicios...")
                    for i in servs:
                        try:
                            print(f"Creando detalle para servicio: {i['code']}")
                            detalle = PRQ1()
                            item = OITM.objects.get(ItemCode=i['code'])
                            proveedor = None
                            if i['proveedor']:
                                proveedor = OCRD.objects.get(CardName=i['proveedor'])
                            cuentaContable = OACT.objects.get(AcctName=i['cuenta_contable'])
                            uni_med = OUOM.objects.get(Code="Sin Unidad")
                            almacen = OWHS.objects.get(WhsName="Sin Almacen")
                            dimension = Dimensiones.objects.get(descripcion=i['dimension'])
                            detalle.NumDoc = encabezado
                            detalle.ItemCode = item
                            detalle.LineVendor = proveedor if proveedor else None
                            detalle.Description = i['description']
                            detalle.Quantity = i['cant']
                            detalle.UnidadMedida = uni_med
                            detalle.Currency = moneda
                            detalle.Almacen = almacen
                            detalle.CuentaMayor = cuentaContable
                            detalle.total = i['precio_total']
                            detalle.totalimpdet = float(i['precio_total']) * (1 + tasa_impuesto)  # Calcular total con impuesto
                            if 'price' in i:
                                try:
                                    detalle.Precio = float(i['price'])
                                    print("Precio asignado:", detalle.Precio)
                                except ValueError:
                                    detalle.Precio = 0.0
                            else:
                                detalle.Precio = 0.0
                                print("Advertencia: 'precio' no encontrado en item:", i)
                            detalle.idDimension = dimension
                            detalle.save()
                            print(f"Detalle de servicio guardado con ID: {detalle.pk}")
                        except Exception as e:
                            print(f"Error al guardar detalle de servicio: {str(e)}")
                            raise

                # Actualizar modelo Series
                if serie:
                    serie.NumeroSiguiente += 1
                    serie.save()
                    print(f"Serie actualizada: {serie.NumeroSiguiente}")
                success_message = "La solicitud de compra se ha guardado correctamente."
                print("Solicitud creada exitosamente")
                send_email_to_validator()
                return render(request, template_name, {'success_message': "La solicitud de compra se ha guardado correctamente."})

        except Exception as e:
            print(f"Error general: {str(e)}")
            print(f"Tipo de error: {type(e)}")
            print(f"Traceback completo: {traceback.format_exc()}")
            msg = f"Error al insertar datos maestros: {str(e)}"  # Corregido
            return render(request, template_name, {'error_message': msg})
            # Considera registrar el error en un archivo de log
            render(request, template_name, {'error_message': msg})
        return redirect(success_url)


def obtener_nombre_serie(request):
    num_serie = request.GET.get('num_serie', None)
    if num_serie:
        try:
            serie = Series.objects.get(CodigoSerie=num_serie)
            return JsonResponse({'nombre_serie': serie.Nombre})
        except OSTA.DoesNotExist:
            return JsonResponse({'error': 'Impuesto no encontrado'}, status=404)
    else:
        return JsonResponse({'error': 'Nombre de impuesto no proporcionado'}, status=400)

def obtener_impuesto(request):
    nombre_impuesto = request.GET.get('nombre_impuesto', None)
    if nombre_impuesto:
        try:
            impuesto = OSTA.objects.get(Name=nombre_impuesto)
            return JsonResponse({'rate': impuesto.Rate})
        except OSTA.DoesNotExist:
            return JsonResponse({'error': 'Impuesto no encontrado'}, status=404)
    else:
        return JsonResponse({'error': 'Nombre de impuesto no proporcionado'}, status=400)
    
def obtener_numero_serie(request):
    serie = request.GET.get('numSerie', None)
    if serie:
        try:
            num = Series.objects.get(Nombre=serie)
            return JsonResponse({'docNum': num.NumeroSiguiente})
        except Series.DoesNotExist:
            return JsonResponse({'error': 'Serie no encontrada'}, status=404)
    else:
        return JsonResponse({'error': 'Nombre de impuesto no proporcionado'}, status=400)
    
    
def obtener_moneda(request):
    today = timezone.now().date()
    moneda = Moneda.objects.filter(TCDate=today)
    # Convert to JSON or a similar format to pass to the template
    monedas_list = list(moneda.values('MonedaAbrev', 'CambioSoles'))
    print(monedas_list)  # Agregar un log para depuración
    return JsonResponse(monedas_list, safe=False)

    
# Metodo obtener LineStatus para calcular total
@login_required(login_url='/login/')
def get_line_details(request):
    if request.method == 'POST':
        doc_entry = request.POST.get('docEntry')
        line_status = request.POST.get('lineStatus').split(',')

        # Obtener la solicitud de compra
        solicitud = get_object_or_404(OPRQ, DocEntry=doc_entry)

        # Obtener los detalles de la solicitud con los estados de línea especificados
        detalles = PRQ1.objects.filter(NumDoc=solicitud, LineStatus__in=line_status)

        # Preparar los datos para la respuesta JSON
        detalles_data = list(detalles.values('ItemCode', 'Description', 'Quantity', 'Precio', 'totalimpdet', 'LineStatus'))

        return JsonResponse(detalles_data, safe=False)
    return JsonResponse({'error': 'Invalid request method'}, status=400)
    

class ListLogistica(ValidatePermissionRequiredMixin2, ListView):
    model = OPRQ
    template_name = 'VistaLogistica/vistaLogistica.html'
    required_groups = 'Jefe_Logistica'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        socioNegocio = OCRD.objects.all()
        contexto = {
            'socio_negocio': socioNegocio,
        }
        return render(request, self.template_name, contexto)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == "searchSolicitudes":
                data = []
                user = self.request.user
                solicitudes = OPRQ.objects.filter(DocStatus__in=['C', 'CP'], TipoDoc='SOL').order_by('DocEntry')
                for solicitud in solicitudes:
                    # Verificar si la solicitud tiene detalles en LineStatus 'L'
                    if PRQ1.objects.filter(NumDoc=solicitud.pk, LineStatus='L').exists():
                        data.append(solicitud.toJSON())
            elif action == "showDetails":
                data = []
                for detalle in PRQ1.objects.filter(NumDoc=request.POST['id'], LineStatus='L'):
                    data.append(detalle.toJSON())
            elif action == "getDetails":
                data = []
                for detalle in PRQ1.objects.filter(NumDoc=request.POST['code'], LineStatus='L'):
                    data.append(detalle.toJSON())
            else:
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Listado de Solicitudes'
        context['entity'] = 'OPRQ'
        return context

    def get_queryset(self):
        return OPRQ.objects.order_by('DocNum')


class ListSolicitudesCompra(ValidatePermissionRequiredMixin2, ListView):
    model = OPRQ
    template_name = 'SolicitudCompra/listar_solicitud_compra.html'
    required_groups = ['Empleado', 'Validador', 'Jefe_De_Area', 'Jefe_de_Presupuestos']

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == "searchSolicitudes":
                estado = request.POST['estado']
                data = []
                user = self.request.user
                if user.groups.filter(name__in=['Administrador', 'Validador']).exists():
                    if estado == '0':
                        solicitudes = OPRQ.objects.order_by('DocEntry')
                    else:
                        solicitudes = OPRQ.objects.filter(DocStatus=estado).order_by('DocEntry')
                elif user.groups.filter(name__in=['Jefe_De_Area']).exists():
                    depto = Departamento.objects.get(Name=user.departamento)
                    if estado == '0':
                        solicitudes = OPRQ.objects.filter(Department=depto.Code).order_by('DocEntry')
                    else:
                        solicitudes = OPRQ.objects.filter(DocStatus=estado).filter(Department=depto.Code).order_by('DocEntry')
                elif user.groups.filter(name__in=['Empleado']).exists():
                    if estado == '0':
                        solicitudes = OPRQ.objects.filter(ReqIdUser=user.id).order_by('DocEntry')
                    else:
                        solicitudes = OPRQ.objects.filter(ReqIdUser=user.id).filter(DocStatus=estado).order_by('DocEntry')
                elif user.groups.filter(name__in=['Jefe_de_Presupuestos']).exists():
                    solicitudes = OPRQ.objects.filter(DocStatus__in=['A', 'CP']).order_by('DocEntry')  # Filtrar por 'A' y 'CP'
                for i in solicitudes:
                    data.append(i.toJSON())
            elif action == "showDetails":
                data = []
                user = self.request.user
                if user.groups.filter(name__in=['Jefe_de_Presupuestos']).exists():
                    for i in PRQ1.objects.filter(NumDoc=request.POST['id'], LineStatus='A'):  # Filtrar por LineStatus 'A'
                        data.append(i.toJSON())
                else:
                    for i in PRQ1.objects.filter(NumDoc=request.POST['id']):
                        data.append(i.toJSON())
            elif action == "getDetails":
                data = []
                user = self.request.user
                if user.groups.filter(name__in=['Jefe_de_Presupuestos']).exists():
                    for i in PRQ1.objects.filter(NumDoc=request.POST['code'], LineStatus='A'):  # Filtrar por LineStatus 'A'
                        data.append(i.toJSON())
                else:
                    for i in PRQ1.objects.filter(NumDoc=request.POST['code']):
                        data.append(i.toJSON())
            else:
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Listado de Solicitudes'
        context['entity'] = 'OPRQ'
        context['edition_permissions'] = self.request.user.has_perm('erp.change_oprq')
        return context

    def get_queryset(self):
        return OPRQ.objects.order_by('DocNum')
    
    
    
class ListContabilizadas(ValidatePermissionRequiredMixin2, ListView):
    model = OPRQ
    template_name = 'SolicitudCompra/listar_contabilizadas.html'
    required_groups = ['Administrador', 'Jefe_de_Presupuestos']

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == "searchSolicitudes":
                data = []
                user = self.request.user
                if user.groups.filter(name__in=['Administrador', 'Jefe_de_Presupuestos']).exists():
                    # Eliminamos la dependencia del parámetro 'estado'
                    solicitudes = OPRQ.objects.filter(DocStatus='C').order_by('DocEntry')  # Solo trae las contabilizadas
                    for i in solicitudes:
                        data.append(i.toJSON())
            elif action == "showDetails":
                data = []
                user = self.request.user
                if user.groups.filter(name__in=['Administrador', 'Jefe_de_Presupuestos']).exists():
                    for i in PRQ1.objects.filter(NumDoc=request.POST['id'], LineStatus__in=['C', 'L']):  # Filtrar por LineStatus 'C' y 'L'
                        data.append(i.toJSON())
            elif action == "getDetails":
                data = []
                user = self.request.user
                if user.groups.filter(name__in=['Administrador', 'Jefe_de_Presupuestos']).exists():
                    for i in PRQ1.objects.filter(NumDoc=request.POST['code'], LineStatus__in=['C', 'L']):  # Filtrar por LineStatus 'C' y 'L'
                        data.append(i.toJSON())
            else:
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Listado de Solicitudes Contabilizadas'
        context['entity'] = 'OPRQ'
        context['edition_permissions'] = self.request.user.has_perm('erp.change_oprq')
        return context

    def get_queryset(self):
        return OPRQ.objects.filter(DocStatus='C').order_by('DocNum')
    
    
    

@login_required
def get_user_groups(request):
    if request.user.is_authenticated:
        user_groups = list(request.user.groups.values_list('name', flat=True))
        return JsonResponse(user_groups, safe=False)
    else:
        return JsonResponse({'error': 'User not authenticated'}, status=401)


##CONTABILIZAR 
def solicitudContabilizar(request, id):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            usuario = data.get('usuario', None)
            items_contabilizados = data.get('arrcheckedProd', [])
            
            if not items_contabilizados:
                return JsonResponse({'error': 'Debe seleccionar al menos un item para contabilizar'}, status=400)

            solicitud = OPRQ.objects.filter(pk=id).first()
            if not solicitud:
                return JsonResponse({'error': 'Solicitud no encontrada'}, status=404)

            with transaction.atomic():
                current_time = timezone.now()
                
                # Actualizar items seleccionados a 'L' y guardar datos de aprobación
                detalles = PRQ1.objects.filter(NumDoc=id, Code__in=items_contabilizados)
                for detalle in detalles:
                    detalle.LineStatus = 'L'
                    detalle.idJefePresupuestos = request.user
                    detalle.DateJefePresupuestos = current_time
                    detalle.save()

                # Verificar si todos los detalles están en 'L'
                todos_contabilizados = not PRQ1.objects.filter(NumDoc=id).exclude(LineStatus='L').exists()
                
                if todos_contabilizados:
                    OPRQ.objects.filter(pk=id).update(DocStatus="C")
                else:
                    OPRQ.objects.filter(pk=id).update(DocStatus="CP")

                # Verificar si todos los detalles están contabilizados y no hay detalles pendientes
                detalles_pendientes = PRQ1.objects.filter(NumDoc=id, LineStatus__in=['A', 'P']).exists()
                if not detalles_pendientes:
                    OPRQ.objects.filter(pk=id).update(DocStatus="C")

                validate = Validaciones()
                validate.codReqUser = usuario
                validate.codValidador = request.user.username
                validate.fecha = current_time
                validate.estado = "Contabilizado"
                validate.save()
                
                send_email_to_user(1)
                return HttpResponse("OK")

        except Exception as e:
            msg = f"Error al insertar datos maestros: {str(e)}"
            return JsonResponse({'error': msg}, status=500)
            
    return JsonResponse({'error': 'Método no permitido'}, status=405)


def solicitudContabilizarMasivo(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            arrSolicitudes = data.get('ids', None)
            if not arrSolicitudes:
                return JsonResponse({'error': 'No se recibieron IDs'}, status=400)
            
            with transaction.atomic():
                current_time = timezone.now()
                
                for id in arrSolicitudes:
                    solicitud_actual = OPRQ.objects.get(pk=id)
                    Solicitud_object = OPRQ.objects.filter(pk=id)
                    
                    # Actualizar items seleccionados a 'L' y guardar datos de aprobación
                    detalles = PRQ1.objects.filter(NumDoc=id, LineStatus='A')
                    for detalle in detalles:
                        detalle.LineStatus = 'L'
                        detalle.idJefePresupuestos = request.user
                        detalle.DateJefePresupuestos = current_time
                        detalle.save()

                    # Verificar si todos los detalles están en 'L'
                    todos_contabilizados = not PRQ1.objects.filter(NumDoc=id).exclude(LineStatus='L').exists()
                    
                    if todos_contabilizados:
                        Solicitud_object.update(DocStatus="C")
                    else:
                        Solicitud_object.update(DocStatus="CP")

                    # Verificar si todos los detalles están contabilizados y no hay detalles pendientes
                    detalles_pendientes = PRQ1.objects.filter(NumDoc=id, LineStatus__in=['A', 'P']).exists()
                    if not detalles_pendientes:
                        Solicitud_object.update(DocStatus="C")

                    validate = Validaciones()
                    usuario = solicitud_actual.ReqIdUser
                    usuario_solicitante = User.objects.get(username=usuario)
                    validate.codReqUser = usuario_solicitante.first_name + ' ' + usuario.last_name
                    validate.codValidador = request.user.username
                    validate.fecha = current_time
                    validate.estado = "Contabilizado"
                    validate.save()
                    
            return HttpResponse("OK")
        except Exception as e:
            msg = f"Error al insertar datos maestros: {str(e)}"
            return JsonResponse({'error': msg}, status=500)
    return JsonResponse({'error': 'Metodo no permitido'}, status=405)
    

def solicitudAprobarMasivo(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            arrSolicitudes = data.get('ids', None)
            checked_prod = data.get('arrcheckedProd', [])
            
            if not arrSolicitudes:
                return JsonResponse({'error': 'No se recibieron IDs'}, status=400)

            with transaction.atomic():
                for id in arrSolicitudes:
                    Solicitud = OPRQ.objects.filter(pk=id)
                    if not Solicitud:
                        return JsonResponse({'error': 'Solicitud no encontrada'}, status=404)

                    detalles = PRQ1.objects.filter(NumDoc=id)
                    if detalles.exists():
                        original_status = {detalle.pk: detalle.LineStatus for detalle in detalles}
                        checked_codes = {item.get('Code') for item in checked_prod}
                    else:
                        return JsonResponse({'error': 'Detalle no encontrado'}, status=404)

                    # 1. Actualizar LineStatus de los detalles y guardar datos de aprobación
                    current_time = timezone.now()
                    for detalle in detalles:
                        if detalle.Code in checked_codes:
                            if detalle.LineStatus != 'A':
                                detalle.LineStatus = 'A'
                                # Guardar datos de aprobación
                                detalle.idAreaGeneral = request.user
                                detalle.DateAreaGeneral = current_time
                                detalle.save()
                        else:
                            if detalle.LineStatus != 'R':
                                detalle.LineStatus = 'R'
                                detalle.save()

                    # 2. Reindexar LineCount_Indexado solo para los detalles aprobados
                    detalles_aprobados = detalles.filter(LineStatus='A').order_by('LineCount')
                    for idx, detalle in enumerate(detalles_aprobados):
                        detalle.LineCount_Indexado = idx
                        detalle.save()

                    # 3. Enviar la solicitud a SAP
                    response = export_data_as_json(id)
                    response_content = json.loads(response.content)
                    error_message = response_content.get('error', 'Error desconocido')

                    # 4. Manejar errores de SAP
                    if response.status_code != 200:
                        for detalle in detalles:
                            detalle.LineStatus = original_status.get(detalle.pk, detalle.LineStatus)
                            # Limpiar datos de aprobación en caso de error
                            if detalle.Code in checked_codes:
                                detalle.idAreaGeneral = None
                                detalle.DateAreaGeneral = None
                            detalle.save()
                        return JsonResponse({'error': error_message}, status=response.status_code)
                    else:
                        # 5. Actualizar el estado de la solicitud y registrar la validación
                        solicitud_actual = OPRQ.objects.get(pk=id)
                        Solicitud_object = OPRQ.objects.filter(pk=id)
                        validate = Validaciones()
                        Solicitud_object.update(DocStatus="A")
                        usuario = solicitud_actual.ReqIdUser
                        usuario_solicitante = User.objects.get(username=usuario)
                        validate.codReqUser = usuario_solicitante.first_name + ' ' + usuario.last_name
                        validate.codValidador = request.user.username
                        validate.fecha = current_time
                        validate.estado = "Aprobado"
                        validate.save()

                # 6. Retornar éxito si todas las solicitudes se aprobaron correctamente
                return JsonResponse({'success': "Éxito"}, status=200)

        except Exception as e:
            msg = f"Error al insertar datos maestros: {str(e)}"
            return JsonResponse({'error': msg}, status=500)

    return JsonResponse({'error': 'Método no permitido'}, status=405)


def solicitudRechazarMasivo(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            arrSolicitudes = data.get('ids', None)
            if not arrSolicitudes:
                return JsonResponse({'error': 'No se recibieron IDs'}, status=400)

            with transaction.atomic():
                for id in arrSolicitudes:
                    solicitud = OPRQ.objects.filter(pk=id).first()
                    if not solicitud:
                        return JsonResponse({'error': f'Solicitud {id} no encontrada'}, status=404)

                    # Obtener todos los detalles de la solicitud
                    detalles = PRQ1.objects.filter(NumDoc=id)
                    if not detalles.exists():
                        return JsonResponse({'error': f'Detalles no encontrados para solicitud {id}'}, status=404)

                    # Actualizar todos los detalles a rechazado
                    detalles.update(LineStatus='R')

                    # Verificar estado de todos los detalles
                    total_detalles = detalles.count()
                    detalles_rechazados = PRQ1.objects.filter(NumDoc=id, LineStatus='R').count()
                    detalles_pendientes_P = PRQ1.objects.filter(NumDoc=id, LineStatus='P').exists()
                    detalles_pendientes_A = PRQ1.objects.filter(NumDoc=id, LineStatus='A').exists()
                    detalles_cerrados = PRQ1.objects.filter(NumDoc=id, LineStatus='C').count()
                    detalles_logistica = PRQ1.objects.filter(NumDoc=id, LineStatus='L').exists()

                    # Determinar el nuevo estado
                    if total_detalles == detalles_rechazados:
                        # Si todos están rechazados
                        OPRQ.objects.filter(pk=id).update(DocStatus="R")
                    elif detalles_pendientes_P:
                        # Si hay items pendientes en estado 'P', mantener DocStatus como 'P'
                        # No hacemos update para mantener el DocStatus actual
                        pass
                    elif not detalles_pendientes_A:
                        if detalles_cerrados + detalles_rechazados == total_detalles:
                            # Si no hay pendientes y todos los demás están cerrados (C)
                            OPRQ.objects.filter(pk=id).update(
                                DocStatus="C",
                                TipoDoc="OC"
                            )
                        elif not detalles_logistica:
                            # Si no hay pendientes ni en logística, pero hay mezcla de C y R
                            OPRQ.objects.filter(pk=id).update(DocStatus="C")

                    # Crear validación
                    validate = Validaciones()
                    validate.codReqUser = f"{solicitud.ReqIdUser.first_name} {solicitud.ReqIdUser.last_name}"
                    validate.codValidador = request.user.username
                    validate.fecha = timezone.now()
                    validate.estado = "Rechazado"
                    validate.save()

                return HttpResponse("OK")

        except Exception as e:
            msg = f"Error al insertar datos maestros: {str(e)}"
            return JsonResponse({'error': msg}, status=500)

    return JsonResponse({'error': 'Método no permitido'}, status=405)

def solicitudRechazarMasivoPres(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            arrSolicitudes = data.get('ids', None)
            if not arrSolicitudes:
                return JsonResponse({'error': 'No se recibieron IDs'}, status=400)

            with transaction.atomic():
                for id in arrSolicitudes:
                    solicitud = OPRQ.objects.filter(pk=id).first()
                    if not solicitud:
                        return JsonResponse({'error': f'Solicitud {id} no encontrada'}, status=404)

                    # Obtener todos los detalles de la solicitud
                    detalles = PRQ1.objects.filter(NumDoc=id)
                    if not detalles.exists():
                        return JsonResponse({'error': f'Detalles no encontrados para solicitud {id}'}, status=404)

                    # Actualizar todos los detalles a rechazado
                    detalles.update(LineStatus='R')

                    # Verificar estado de todos los detalles
                    total_detalles = detalles.count()
                    detalles_rechazados = PRQ1.objects.filter(NumDoc=id, LineStatus='R').count()
                    detalles_pendientes_P = PRQ1.objects.filter(NumDoc=id, LineStatus='P').exists()
                    detalles_pendientes_A = PRQ1.objects.filter(NumDoc=id, LineStatus='A').exists()
                    detalles_cerrados = PRQ1.objects.filter(NumDoc=id, LineStatus='C').count()
                    detalles_logistica = PRQ1.objects.filter(NumDoc=id, LineStatus='L').exists()

                    # Determinar el nuevo estado
                    if total_detalles == detalles_rechazados:
                        # Si todos están rechazados
                        OPRQ.objects.filter(pk=id).update(DocStatus="R")
                    elif detalles_pendientes_P:
                        # Si hay items pendientes en estado 'P', mantener DocStatus como 'P'
                        # No hacemos update para mantener el DocStatus actual
                        pass
                    elif not detalles_pendientes_A:
                        if detalles_cerrados + detalles_rechazados == total_detalles:
                            # Si no hay pendientes y todos los demás están cerrados (C)
                            OPRQ.objects.filter(pk=id).update(
                                DocStatus="C",
                                TipoDoc="OC"
                            )
                        elif not detalles_logistica:
                            # Si no hay pendientes ni en logística, pero hay mezcla de C y R
                            OPRQ.objects.filter(pk=id).update(DocStatus="C")

                    # Crear validación
                    validate = Validaciones()
                    validate.codReqUser = f"{solicitud.ReqIdUser.first_name} {solicitud.ReqIdUser.last_name}"
                    validate.codValidador = request.user.username
                    validate.fecha = timezone.now()
                    validate.estado = "Rechazado"
                    validate.save()

                return HttpResponse("OK")

        except Exception as e:
            msg = f"Error al insertar datos maestros: {str(e)}"
            return JsonResponse({'error': msg}, status=500)

    return JsonResponse({'error': 'Método no permitido'}, status=405)


def solicitudAprobar(request, id):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            checked_prod = data.get('arrcheckedProd', [])
            usuario = data.get('usuario', None)
            Solicitud = OPRQ.objects.filter(pk=id)
            
            if not Solicitud:
                return JsonResponse({'error': 'Solicitud no encontrada'}, status=404)

            with transaction.atomic():
                detalles = PRQ1.objects.filter(NumDoc=id)
                if detalles.exists():
                    original_status = {detalle.pk: detalle.LineStatus for detalle in detalles}
                    checked_codes = {item.get('Code') for item in checked_prod}
                else:
                    return JsonResponse({'error': 'Detalle no encontrado'}, status=404)

                # 1. Actualizar LineStatus de los detalles y guardar aprobación
                current_time = timezone.now()
                for detalle in detalles:
                    if detalle.Code in checked_codes:
                        if detalle.LineStatus != 'A':
                            detalle.LineStatus = 'A'
                            # Guardar datos de aprobación
                            detalle.idAreaGeneral = request.user
                            detalle.DateAreaGeneral = current_time
                            detalle.save()
                    else:
                        if detalle.LineStatus != 'R':
                            detalle.LineStatus = 'R'
                            detalle.save()

                # 2. Reindexar LineCount_Indexado solo para los detalles aprobados (LineStatus = 'A')
                detalles_aprobados = detalles.filter(LineStatus='A').order_by('LineCount')
                for idx, detalle in enumerate(detalles_aprobados):
                    detalle.LineCount_Indexado = idx  # Reindexar desde 0
                    detalle.save()

                # 3. Enviar la solicitud a SAP
                response = export_data_as_json(id)
                response_content = json.loads(response.content)
                error_message = response_content.get('error', 'Error desconocido')

                # 4. Manejar errores de SAP
                if response.status_code != 200:
                    for detalle in detalles:
                        detalle.LineStatus = original_status.get(detalle.pk, detalle.LineStatus)
                        # Limpiar datos de aprobación en caso de error
                        if detalle.Code in checked_codes:
                            detalle.idAreaGeneral = None
                            detalle.DateAreaGeneral = None
                        detalle.save()
                    return JsonResponse({'error': error_message}, status=response.status_code)
                else:
                    validate = Validaciones()
                    Solicitud.update(DocStatus="A")
                    validate.codReqUser = usuario
                    validate.codValidador = request.user.username
                    validate.fecha = current_time
                    validate.estado = "Aprobado"
                    validate.save()
                    send_email_to_user(1)
                    return JsonResponse({'success': "Éxito"}, status=200)

        except Exception as e:
            msg = f"Error al insertar datos maestros: {str(e)}"
            return JsonResponse({'error': msg}, status=500)
    
    return JsonResponse({'error': 'Método no permitido'}, status=405)


def solicitudRechazar(request, id):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            usuario = data.get('usuario', None)
            items_rechazados = data.get('arrcheckedProd', [])
            
            if not items_rechazados:
                return JsonResponse({'error': 'Debe seleccionar al menos un item para rechazar'}, status=400)

            solicitud = OPRQ.objects.filter(pk=id).first()
            if not solicitud:
                return JsonResponse({'error': 'Solicitud no encontrada'}, status=404)

            with transaction.atomic():
                # Actualizar items seleccionados
                detalles = PRQ1.objects.filter(NumDoc=id, Code__in=items_rechazados)
                detalles_actualizados = detalles.update(LineStatus='R')

                # Verificar estado de todos los detalles
                total_detalles = PRQ1.objects.filter(NumDoc=id).count()
                detalles_rechazados = PRQ1.objects.filter(NumDoc=id, LineStatus='R').count()
                detalles_pendientes_P = PRQ1.objects.filter(NumDoc=id, LineStatus='P').exists()
                detalles_pendientes_A = PRQ1.objects.filter(NumDoc=id, LineStatus='A').exists()
                detalles_cerrados = PRQ1.objects.filter(NumDoc=id, LineStatus='C').count()
                detalles_logistica = PRQ1.objects.filter(NumDoc=id, LineStatus='L').exists()
                
                # Determinar el nuevo estado
                if total_detalles == detalles_rechazados:
                    # Si todos están rechazados
                    OPRQ.objects.filter(pk=id).update(DocStatus="R")
                elif detalles_pendientes_P:
                    # Si hay items pendientes en estado 'P', mantener DocStatus como 'P'
                    # No hacemos update para mantener el DocStatus actual
                    pass
                elif not detalles_pendientes_A:
                    if detalles_cerrados + detalles_rechazados == total_detalles:
                        # Si no hay pendientes y todos los demás están cerrados (C)
                        OPRQ.objects.filter(pk=id).update(
                            DocStatus="C",
                            TipoDoc="OC"
                        )
                    elif not detalles_logistica:
                        # Si no hay pendientes ni en logística, pero hay mezcla de C y R
                        OPRQ.objects.filter(pk=id).update(DocStatus="C")
                    
                validate = Validaciones()
                validate.codReqUser = usuario
                validate.codValidador = request.user.username
                validate.fecha = timezone.now()
                validate.estado = "Rechazado"
                validate.save()
                
                send_email_to_user(0)
                return HttpResponse("OK")

        except Exception as e:
            msg = f"Error al insertar datos maestros: {str(e)}"
            return JsonResponse({'error': msg}, status=500)
            
    return JsonResponse({'error': 'Método no permitido'}, status=405)


def solicitudRechazarPres(request, id):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            usuario = data.get('usuario', None)
            items_rechazados = data.get('arrcheckedProd', [])
            
            if not items_rechazados:
                return JsonResponse({'error': 'Debe seleccionar al menos un item para rechazar'}, status=400)

            solicitud = OPRQ.objects.filter(pk=id).first()
            if not solicitud:
                return JsonResponse({'error': 'Solicitud no encontrada'}, status=404)

            with transaction.atomic():
                # Actualizar items seleccionados
                detalles = PRQ1.objects.filter(NumDoc=id, Code__in=items_rechazados)
                detalles_actualizados = detalles.update(LineStatus='R')

                # Verificar estado de todos los detalles
                total_detalles = PRQ1.objects.filter(NumDoc=id).count()
                detalles_rechazados = PRQ1.objects.filter(NumDoc=id, LineStatus='R').count()
                detalles_pendientes_P = PRQ1.objects.filter(NumDoc=id, LineStatus='P').exists()
                detalles_pendientes_A = PRQ1.objects.filter(NumDoc=id, LineStatus='A').exists()
                detalles_cerrados = PRQ1.objects.filter(NumDoc=id, LineStatus='C').count()
                detalles_logistica = PRQ1.objects.filter(NumDoc=id, LineStatus='L').exists()
                
                # Determinar el nuevo estado
                if total_detalles == detalles_rechazados:
                    # Si todos están rechazados
                    OPRQ.objects.filter(pk=id).update(DocStatus="R")
                elif detalles_pendientes_P:
                    # Si hay items pendientes en estado 'P', mantener DocStatus como 'P'
                    # No hacemos update para mantener el DocStatus actual
                    pass
                elif not detalles_pendientes_A:
                    if detalles_cerrados + detalles_rechazados == total_detalles:
                        # Si no hay pendientes y todos los demás están cerrados (C)
                        OPRQ.objects.filter(pk=id).update(
                            DocStatus="C",
                            TipoDoc="OC"
                        )
                    elif not detalles_logistica:
                        # Si no hay pendientes ni en logística, pero hay mezcla de C y R
                        OPRQ.objects.filter(pk=id).update(DocStatus="C")
                    
                validate = Validaciones()
                validate.codReqUser = usuario
                validate.codValidador = request.user.username
                validate.fecha = timezone.now()
                validate.estado = "Rechazado"
                validate.save()
                
                send_email_to_user(0)
                return HttpResponse("OK")

        except Exception as e:
            msg = f"Error al insertar datos maestros: {str(e)}"
            return JsonResponse({'error': msg}, status=500)
            
    return JsonResponse({'error': 'Método no permitido'}, status=405)


# def export_data_as_json(id):
#     solicitudes = OPRQ.objects.filter(pk=id)

#     if not solicitudes:
#         return JsonResponse({'error': 'No se encontraron solicitudes'}, status=404)

#     data = []
#     for solicitud in solicitudes:
#         if not solicitudes:
#             return  # No hay solicitudes que procesar
#         oprq = {
#             "Requester": solicitud.ReqCode if solicitud.ReqCode else '1',
#             "ReqType": solicitud.ReqType,
#             "DocType": "dDocument_Items" if solicitud.DocType == 'I' else ("dDocument_Service" if solicitud.DocType == 'S' else None),
#             "DocDate": solicitud.DocDate,
#             "DocCurrency": solicitud.moneda.MonedaAbrev,
#             "Comments": solicitud.Comments,
#             "TaxDate": solicitud.DocDate,
#             "Series": solicitud.Serie,
#             "RequriedDate": solicitud.ReqDate,
#             "DocumentLines": []
#         }
#         detalle = PRQ1.objects.filter(NumDoc=solicitud.DocEntry)
#         for det in detalle:
#             # Solo agregamos la línea si el estado de la línea es "A" (Activo)
#             if det.LineStatus == 'A':
#                 if solicitud.DocType == 'I':  # Tipo de documento "Items"
#                     detalle_list = {
#                         "LineNum": det.LineCount_Indexado,
#                         'ItemCode': det.ItemCode.ItemCode,
#                         'LineVendor': det.LineVendor.CardCode if det.LineVendor else None,  # Se agrega solo si LineVendor no es nulo
#                         "TaxCode": solicitud.TaxCode.Code,
#                         'Quantity': det.Quantity,
#                         "UnitPrice": det.Precio,
#                         'CostingCode': det.idDimension.descripcion if det.idDimension else 'null',
#                         'Currency': det.Currency.MonedaAbrev if det.Currency else 'null'
#                     }
#                     # Si LineVendor es None, lo eliminamos del diccionario antes de agregarlo
#                     if detalle_list['LineVendor'] is None:
#                         del detalle_list['LineVendor']
#                     oprq['DocumentLines'].append(detalle_list)

#                 elif solicitud.DocType == 'S':  # Tipo de documento "Service"
#                     detalle_list = {
#                         "ItemDescription": det.ItemCode.ItemCode,
#                         'LineVendor': det.LineVendor.CardCode if det.LineVendor else None,  # Se agrega solo si LineVendor no es nulo
#                         "RequiredDate": solicitud.ReqDate,
#                         "TaxCode": solicitud.TaxCode.Code,
#                         'Quantity': det.Quantity,
#                         "Price": det.Precio,
#                         "UnitPrice": det.Precio,
#                         "DocTotalFC": det.Precio * det.Quantity,
#                         "AccountCode": det.CuentaMayor.AcctCode,
#                         'CostingCode': det.idDimension.descripcion if det.idDimension else 'null',
#                         'Currency': det.Currency.MonedaAbrev if det.Currency else 'null'
#                     }
#                     # Si LineVendor es None, lo eliminamos del diccionario antes de agregarlo
#                     if detalle_list['LineVendor'] is None:
#                         del detalle_list['LineVendor']
#                     oprq['DocumentLines'].append(detalle_list)

#         data.append(oprq)

#     json_data = json.dumps(data[0], indent=2, default=lambda o: o.isoformat() if isinstance(o, date) else None)
#     print(json_data)
#     response = data_sender(json_data, id)
#     if isinstance(response, JsonResponse):
#         return response
#     return JsonResponse({'error': 'Error al enviar datos'}, status=500)

def export_data_as_json(id):
    solicitudes = OPRQ.objects.filter(pk=id)

    if not solicitudes:
        return JsonResponse({'error': 'No se encontraron solicitudes'}, status=404)

    data = []
    for solicitud in solicitudes:
        if not solicitudes:
            return  # No hay solicitudes que procesar
        oprq = {
            "Requester": solicitud.ReqCode if solicitud.ReqCode else '1',
            "ReqType": solicitud.ReqType,
            "DocType": "dDocument_Items" if solicitud.DocType == 'I' else ("dDocument_Service" if solicitud.DocType == 'S' else None),
            "DocDate": solicitud.DocDate,
            "DocCurrency": solicitud.moneda.MonedaAbrev,
            "Comments": solicitud.Comments,
            "TaxDate": solicitud.DocDate,
            "Series": solicitud.Serie,
            "RequriedDate": solicitud.ReqDate,
            "DocumentLines": []
        }
        detalle = PRQ1.objects.filter(NumDoc=solicitud.DocEntry)
        for det in detalle:
            # Solo agregamos la línea si el estado de la línea es diferente de "R" (Rechazado)
            if det.LineStatus != 'R':
                if solicitud.DocType == 'I':  # Tipo de documento "Items"
                    detalle_list = {
                        "LineNum": det.LineCount_Indexado,
                        'ItemCode': det.ItemCode.ItemCode,
                        'LineVendor': det.LineVendor.CardCode if det.LineVendor else None,  # Se agrega solo si LineVendor no es nulo
                        "TaxCode": solicitud.TaxCode.Code,
                        'Quantity': det.Quantity,
                        "UnitPrice": det.Precio,
                        'CostingCode': det.idDimension.descripcion if det.idDimension else 'null',
                        'Currency': det.Currency.MonedaAbrev if det.Currency else 'null'
                    }
                    # Si LineVendor es None, lo eliminamos del diccionario antes de agregarlo
                    if detalle_list['LineVendor'] is None:
                        del detalle_list['LineVendor']
                    oprq['DocumentLines'].append(detalle_list)

                elif solicitud.DocType == 'S':  # Tipo de documento "Service"
                    detalle_list = {
                        "ItemDescription": det.ItemCode.ItemCode,
                        'LineVendor': det.LineVendor.CardCode if det.LineVendor else None,  # Se agrega solo si LineVendor no es nulo
                        "RequiredDate": solicitud.ReqDate,
                        "TaxCode": solicitud.TaxCode.Code,
                        'Quantity': det.Quantity,
                        "Price": det.Precio,
                        "UnitPrice": det.Precio,
                        "DocTotalFC": det.Precio * det.Quantity,
                        "AccountCode": det.CuentaMayor.AcctCode,
                        'CostingCode': det.idDimension.descripcion if det.idDimension else 'null',
                        'Currency': det.Currency.MonedaAbrev if det.Currency else 'null'
                    }
                    # Si LineVendor es None, lo eliminamos del diccionario antes de agregarlo
                    if detalle_list['LineVendor'] is None:
                        del detalle_list['LineVendor']
                    oprq['DocumentLines'].append(detalle_list)

        data.append(oprq)

    json_data = json.dumps(data[0], indent=2, default=lambda o: o.isoformat() if isinstance(o, date) else None)
    print(json_data)
    response = data_sender(json_data, id)
    if isinstance(response, JsonResponse):
        return response
    return JsonResponse({'error': 'Error al enviar datos'}, status=500)


def data_sender(json_data, id):
    url_session = "https://CFR-I7-1:50000/b1s/v1/Login"

    payload_session = json.dumps({
        "CompanyDB": "BDPRUEBASOCL",
        "Password": "m1r1",
        "UserName": "manager"
    })
    headers_session = {
    'Content-Type': 'application/json',
    'Cookie': 'B1SESSION=d266d95e-4e81-11ef-8000-b42e99e90cf9; ROUTEID=.node3'
    }

    response_session = requests.request("POST", url_session, headers=headers_session, data=payload_session, verify=False)

    if response_session.status_code == 200:
        # Parsear la respuesta JSON
        response_json = response_session.json()
    
        # Acceder a los valores del JSON
        company_db = response_json.get('SessionId')
    else:
        print(f"Error en la solicitud: {response_session.status_code}")

    url = "https://CFR-I7-1:50000/b1s/v1/PurchaseRequests"
    cookie = 'B1SESSION=' + company_db +'; ROUTEID=.node3'
    headers = {
        'Content-Type': 'application/json',
        'Cookie': cookie
    }
    response = requests.request("POST", url, headers=headers, data=json_data, verify=False)
        
    if response.status_code != 201:
        # Cargar el texto JSON en un diccionario
        response_dict = json.loads(response.text)
        # Acceder al campo 'value'
        value_message = response_dict['error']['message']['value']
        error_message = f"Error en la solicitud de PurchaseRequests: {response.status_code} - {response.text}"
        return JsonResponse({'error': value_message}, status=response.status_code)

    response_JSON = response.json()
    if response_JSON:
        doc_entry = response_JSON.get('DocEntry', None)
        solicitud = OPRQ.objects.filter(pk=id)
        if solicitud.exists():
            for detalle in solicitud:
                detalle.DocNumSAP =  doc_entry
                detalle.save()
    else:
        print("La respuesta JSON está vacía.")
        
    return JsonResponse({'message': 'Data sent successfully'})


# METODO LOGISTICA - PRODUCTOS A OC
def export_data_as_jsonProductos(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            items_data = data.get('items', [])
            proveedor = data.get('proveedor', None)

            if not items_data:
                return JsonResponse({'error': 'No se enviaron productos.'}, status=400)

            if not proveedor:
                return JsonResponse({'error': 'No se especificó un proveedor.'}, status=400)

            items_codes = [item['Code'] for item in items_data]
            detalles = PRQ1.objects.filter(Code__in=items_codes).select_related(
                'NumDoc', 'ItemCode', 'Currency', 'UnidadMedida', 'Almacen', 
                'CuentaMayor', 'idDimension', 'NumDoc__moneda', 'NumDoc__TaxCode'
            )

            if not detalles:
                return JsonResponse({'error': 'No se encontraron detalles para los códigos proporcionados.'}, status=400)

            solicitud = detalles.first().NumDoc

            # Primero crear el JSON para SAP
            oprq = {
                "DocType": "dDocument_Items",
                "DocDate": solicitud.DocDate.isoformat(),
                "DocDueDate": solicitud.DocDueDate.isoformat(),
                "TaxDate": solicitud.DocDate.isoformat(),
                "CardCode": proveedor,
                "DocCurrency": solicitud.moneda.MonedaAbrev,
                "Series": 117,
                "DocumentLines": []
            }

            for idx, detalle in enumerate(detalles):
                item_data = next((item for item in items_data if str(item['Code']) == str(detalle.Code)), None)
                if item_data:
                    oprq["DocumentLines"].append({
                        "LineNum": idx,
                        "ItemCode": detalle.ItemCode.ItemCode,
                        "ItemDescription": detalle.Description,
                        "Quantity": item_data['Quantity'],
                        "UnitPrice": detalle.Precio,
                        "Currency": detalle.Currency.MonedaAbrev,
                        "WarehouseCode": detalle.Almacen.WhsCode,
                        "TaxCode": solicitud.TaxCode.Code,
                        "CostingCode": detalle.idDimension.descripcion if detalle.idDimension else None,
                        "BaseType": 1470000113,
                        "BaseEntry": detalle.NumDoc.DocNumSAP,
                        "BaseLine": detalle.LineCount_Indexado,
                    })

            json_data = json.dumps(oprq, indent=2)
            print("JSON generado para Productos para enviar:", json_data)
            
            # Intentar migración a SAP
            response = data_sender_productos(json_data, solicitud)

            if isinstance(response, dict) and response.get('status') == 'success' and response.get('doc_entry'):
                doc_entry_sap = response['doc_entry']
                print(f"DocEntry a usar: {doc_entry_sap}")

                # Solo si la migración a SAP fue exitosa, procedemos a actualizar la BD
                with transaction.atomic():
                    try:
                        # 1. Crear orden de compra en OCC y OCD1 (inicialmente con DocNumSAP en NULL)
                        orden_compra_cabecera = guardar_orden_compra_oc_producto(
                            detalles_seleccionados=detalles,
                            solicitud=solicitud,
                            tipo='I',
                            proveedor=proveedor,
                            items_data=items_data,
                            request=request
                        )

                        # 2. Actualizar DocNumSAPOC en la cabecera
                        orden_compra_cabecera.DocNumSAPOC = doc_entry_sap
                        orden_compra_cabecera.save()

                        # 3. Actualizar DocNumSAPOCD en los detalles
                        detalles_ocd1 = OCD1.objects.filter(NumDocOCD=orden_compra_cabecera)
                        for detalle_ocd1 in detalles_ocd1:
                            detalle_ocd1.DocNumSAPOCD = doc_entry_sap
                            detalle_ocd1.save()

                        # 4. Actualizar los detalles en PRQ1
                        for detalle in detalles:
                            item_data = next((item for item in items_data if str(item['Code']) == str(detalle.Code)), None)
                            if item_data:
                                detalle.Quantity_rest = item_data['Quantity_rest']
                                detalle.total_rest = item_data['total_rest']
                                if detalle.Quantity_rest == 0:
                                    detalle.LineStatus = 'C'
                                detalle.save()

                        # 5. Verificar detalles pendientes y actualizar TipoDoc
                        detalles_asociados = PRQ1.objects.filter(NumDoc=solicitud.DocEntry)
                        detalles_pendientes = detalles_asociados.filter(
                            Q(LineStatus__in=['A', 'L']) | Q(Quantity_rest__gt=0)
                        ).exclude(LineStatus='R').exists()

                        solicitud.TipoDoc = 'OC' if not detalles_pendientes else 'SOL'
                        solicitud.save()

                        return JsonResponse({'message': 'Producto enviado y guardado correctamente.'}, status=200)

                    except Exception as e:
                        # Si algo falla durante la actualización de la BD, hacer rollback
                        transaction.set_rollback(True)
                        raise Exception(f"Error al actualizar la base de datos: {str(e)}")

            else:
                # Si la migración a SAP falló, no se hace ningún cambio en la BD
                error_msg = f"Error en SAP: {response.get('error', 'Error desconocido')}"
                print(error_msg)
                return JsonResponse({'error': error_msg}, status=500)

        except Exception as e:
            print(f"ERROR GENERAL: {str(e)}")
            print("Traceback completo:")
            print(traceback.format_exc())
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Método no permitido'}, status=405)


def data_sender_productos(json_data, solicitud):
    url_session = "https://CFR-I7-1:50000/b1s/v1/Login"

    payload_session = json.dumps({
        "CompanyDB": "BDPRUEBASOCL",
        "Password": "m1r1",
        "UserName": "manager"
    })
    headers_session = {
        'Content-Type': 'application/json',
    }

    session = requests.Session()

    # Intentar iniciar sesión hasta 5 veces
    for attempt in range(5):
        try:
            response_session = session.post(url_session, headers=headers_session, data=payload_session, verify=False)

            if response_session.status_code == 200:
                session_cookie = response_session.cookies.get('B1SESSION')
                route_id_cookie = response_session.cookies.get('ROUTEID', '.node1')  # Valor por defecto si es None
                
                # Verificar que ambas cookies existan
                if not session_cookie or not route_id_cookie:
                    print(f"Intento {attempt + 1}: Cookies incompletas - B1SESSION: {session_cookie}, ROUTEID: {route_id_cookie}")
                    if attempt == 4:
                        return {
                            'status': 'error',
                            'error': 'No se pudieron obtener las cookies de sesión completas',
                            'status_code': 500
                        }
                    time.sleep(2)
                    continue

                cookie_string = f'B1SESSION={session_cookie}; ROUTEID={route_id_cookie}'
                print("Inicio de sesión exitoso!")
                print(f"Código de estado de la sesión: {response_session.status_code}")
                print(f"Cookies de sesión: {cookie_string}")
                
                # Intentar la llamada a PurchaseOrders inmediatamente después del login
                url = "https://CFR-I7-1:50000/b1s/v1/PurchaseOrders"
                headers = {
                    'Content-Type': 'application/json',
                    'Cookie': cookie_string
                }

                try:
                    print(f"Enviando datos a SAP: {json_data}")
                    response = session.post(url, headers=headers, data=json_data, verify=False)

                    if response.status_code == 201:
                        try:
                            response_json = response.json()
                            doc_entry = response_json.get('DocEntry')
                            print(f"DocEntry extraído (Productos): {doc_entry}")
                            
                            if doc_entry:
                                return {
                                    'status': 'success',
                                    'doc_entry': doc_entry,
                                    'response': response_json
                                }
                        except json.JSONDecodeError:
                            if attempt < 4:  # Si no es el último intento, continuar el bucle
                                print(f"Error al decodificar respuesta en intento {attempt + 1}, reintentando...")
                                time.sleep(2)
                                continue
                            return {
                                'status': 'error',
                                'error': f"Error al decodificar la respuesta de SAP: {response.text}",
                                'status_code': 500
                            }
                    else:
                        if attempt < 4:  # Si no es el último intento, continuar el bucle
                            print(f"Error en intento {attempt + 1}, reintentando...")
                            time.sleep(2)
                            continue
                        
                        try:
                            response_dict = response.json()
                            value_message = response_dict.get('error', {}).get('message', {}).get('value', 'Error desconocido')
                        except json.JSONDecodeError:
                            value_message = f"Error al decodificar la respuesta: {response.text}"
                        
                        return {
                            'status': 'error',
                            'error': value_message,
                            'status_code': response.status_code
                        }

                except requests.RequestException as e:
                    if attempt < 4:
                        print(f"Error de conexión en intento {attempt + 1}, reintentando...")
                        time.sleep(2)
                        continue
                    return {
                        'status': 'error',
                        'error': f"Error en la conexión con SAP: {str(e)}",
                        'status_code': 500
                    }

            else:
                print(f"Intento {attempt + 1} fallido: Error en la solicitud de sesión: {response_session.status_code} - {response_session.text}")
                if attempt == 4:
                    return {
                        'status': 'error',
                        'error': f"Error al iniciar sesión después de 5 intentos: {response_session.status_code}",
                        'status_code': 500
                    }
                time.sleep(2)

        except requests.RequestException as e:
            print(f"Error en el intento {attempt + 1}: {str(e)}")
            if attempt == 4:
                return {
                    'status': 'error',
                    'error': f"Error al intentar iniciar sesión después de 5 intentos: {str(e)}",
                    'status_code': 500
                }
            time.sleep(2)

    return {
        'status': 'error',
        'error': 'No se pudo completar la operación después de 5 intentos',
        'status_code': 500
    }


def guardar_orden_compra_oc_producto(detalles_seleccionados, solicitud, tipo, proveedor, items_data, request):
    try:
        print(f"Items data recibidos: {items_data}")  # Log para debugging
        
        # Buscar el proveedor en la base de datos
        proveedor_instance = OCRD.objects.get(CardCode=proveedor)
    except OCRD.DoesNotExist:
        raise Exception(f'El proveedor con código {proveedor} no existe.')

    # Obtener la serie de OrdenCompra y el siguiente número
    serie_instance = Series.objects.get(Nombre='OrdenCompra')
    doc_num_oc = serie_instance.NumeroSiguiente

    # Verificar que items_data no sea None y sea una lista
    if not items_data or not isinstance(items_data, list):
        raise Exception('No se recibieron datos de items válidos')

    # Calcular el TotalOC usando las cantidades seleccionadas del frontend
    total_oc = 0
    for detalle in detalles_seleccionados:
        # Encontrar el item correspondiente en items_data
        item_data = next(
            (item for item in items_data if str(item['Code']) == str(detalle.Code)), 
            None
        )
        if item_data:
            total_oc += item_data['Quantity'] * detalle.Precio

    # Determinar el TotalImpuestosOC
    if solicitud.TaxCode.Code == "IGV":
        total_impuestos_oc = total_oc * 0.18
    else:
        total_impuestos_oc = solicitud.TotalImp

    orden_compra_cabecera = OCC.objects.create(
        DocNumOC=doc_num_oc,
        SerieOC=serie_instance,
        SolicitanteOC=solicitud.ReqIdUser,
        DocTypeOC=tipo,
        DocDateOC=solicitud.DocDate,
        DocDueDateOC=solicitud.DocDueDate,
        SystemDateOC=date.today(),
        ProveedorOC=proveedor_instance,
        MonedaOC=solicitud.moneda,
        TaxCodeOC=solicitud.TaxCode,
        TotalOC=total_oc,
        TotalImpuestosOC=total_impuestos_oc + total_oc,
        CommentsOC=solicitud.Comments,
        DocNumSAPOC=None  # Inicialmente NULL, se actualizará después
    )

    # Crear los detalles en OCD1
    current_time = timezone.now()
    detalles_ocd1 = []
    for detalle in detalles_seleccionados:
        # Encontrar el item correspondiente en items_data
        item_data = next(
            (item for item in items_data if str(item['Code']) == str(detalle.Code)), 
            None
        )
        
        if not item_data:
            print(f"No se encontró item_data para el detalle con Code: {detalle.Code}")
            continue
        
        # Primero actualizar PRQ1 con los datos de logística
        detalle.idLogistica = request.user
        detalle.DateLogistica = current_time
        detalle.save()

        detalle_ocd1 = OCD1.objects.create(
            NumDocOCD=orden_compra_cabecera,
            ItemCodeOCD=detalle.ItemCode,
            LineVendorOCD=proveedor_instance,
            DescriptionOCD=detalle.Description,
            QuantityOCD=item_data['Quantity'],
            UnidadMedidaOCD=detalle.UnidadMedida,
            AlmacenOCD=detalle.Almacen,
            CuentaMayorOCD=detalle.CuentaMayor,
            PrecioOCD=detalle.Precio,
            TotalOCD=item_data['Quantity'] * detalle.Precio,
            LineStatusOCD='C' if item_data['Quantity_rest'] == 0 else 'L',
            DimensionOCD=detalle.idDimension,
            DocNumSAPOCD=None,  # Inicialmente NULL, se actualizará después
            BaseEntryOCD=detalle.NumDoc.DocNumSAP,
            BaseLineOCD=detalle.LineCount_Indexado,
            DocEntryOCD=detalle.NumDoc.DocEntry,
            
            idAreaGeneralOCD=detalle.idAreaGeneral,
            DateAreaGeneralOCD=detalle.DateAreaGeneral,
            idJefePresupuestosOCD=detalle.idJefePresupuestos,
            DateJefePresupuestosOCD=detalle.DateJefePresupuestos,
            idLogisticaOCD=request.user,
            DateLogisticaOCD=current_time
        )
        detalles_ocd1.append(detalle_ocd1)

    # Incrementar el NumeroSiguiente en la serie
    serie_instance.NumeroSiguiente += 1
    serie_instance.save()

    return orden_compra_cabecera




# METODO LOGISTICA - SERVICIOS A OC - NUEVO CON SERIE
def export_data_as_jsonServicios(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            print("Datos recibidos:", data)  # Añadir esta línea para depuración
            items_data = data.get('items', [])
            proveedor_servicio = data.get('proveedorServicio', None)  # Cambiado a 'proveedorServicio'

            if not items_data:
                return JsonResponse({'error': 'No se enviaron servicios.'}, status=400)

            items_codes = [item['Code'] for item in items_data]

            detalles = PRQ1.objects.filter(Code__in=items_codes).select_related(
                'NumDoc', 'ItemCode', 'Currency', 'CuentaMayor', 'idDimension', 
                'NumDoc__moneda', 'NumDoc__TaxCode', 'LineVendor'
            )

            if not detalles:
                return JsonResponse({'error': 'No se encontraron detalles para los códigos proporcionados.'}, status=400)

            solicitud = detalles.first().NumDoc

            # Determinar el proveedor
            if proveedor_servicio:
                proveedor = proveedor_servicio
            elif primera_detalle := detalles.first().LineVendor:
                proveedor = primera_detalle.CardCode
            else:
                return JsonResponse({'error': 'No se pudo determinar el proveedor para los servicios.'}, status=400)

            # Generar JSON para SAP primero
            oprq = {
                "DocType": "dDocument_Service",
                "DocDate": solicitud.DocDate.isoformat(),
                "DocDueDate": solicitud.DocDueDate.isoformat(),
                "TaxDate": solicitud.DocDate.isoformat(),
                "CardCode": proveedor,
                "DocCurrency": solicitud.moneda.MonedaAbrev,
                "Series": 117,
                "DocumentLines": []
            }

            for idx, detalle in enumerate(detalles):
                oprq["DocumentLines"].append({
                    "LineNum": idx,
                    "ItemDescription": detalle.Description,
                    "Quantity": detalle.Quantity,
                    "Price": detalle.Precio,
                    "Currency": detalle.Currency.MonedaAbrev,
                    "TaxCode": solicitud.TaxCode.Code,
                    "CostingCode": detalle.idDimension.descripcion if detalle.idDimension else None,
                    "UnitPrice": detalle.Precio,
                    "DocTotal": detalle.Precio * detalle.Quantity,
                    "BaseType": 1470000113,
                    "BaseEntry": detalle.NumDoc.DocNumSAP,
                    "BaseLine": detalle.LineCount_Indexado,
                })

            json_data = json.dumps(oprq, indent=2)
            print("JSON generado para Servicios para enviar:", json_data)
            
            # Intentar migración a SAP
            response = data_sender_servicios(json_data, solicitud)

            if response.get('status') == 'success':
                # Solo si la migración a SAP fue exitosa, procedemos con los cambios en la BD
                with transaction.atomic():
                    try:
                        # 1. Crear orden de compra en OCC y OCD1
                        orden_compra_cabecera = guardar_orden_compra_oc_servicio(
                            detalles_seleccionados=detalles,
                            solicitud=solicitud,
                            tipo='S',
                            proveedor=proveedor,
                            request=request
                        )

                        # 2. Actualizar DocNumSAPOC en la cabecera
                        doc_entry_sap = response.get('doc_entry')
                        orden_compra_cabecera.DocNumSAPOC = doc_entry_sap
                        orden_compra_cabecera.save()

                        # 3. Actualizar DocNumSAPOCD en los detalles
                        detalles_ocd1 = OCD1.objects.filter(NumDocOCD=orden_compra_cabecera)
                        for detalle_ocd1 in detalles_ocd1:
                            detalle_ocd1.DocNumSAPOCD = doc_entry_sap
                            detalle_ocd1.save()

                        # 4. Actualizar LineStatus en PRQ1 y TipoDoc en OPRQ
                        for detalle in detalles:
                            detalle.LineStatus = 'C'
                            detalle.save()

                        # 5. Verificar si hay otros detalles pendientes antes de cambiar TipoDoc
                        detalles_asociados = PRQ1.objects.filter(NumDoc=solicitud.DocEntry)
                        detalles_pendientes = detalles_asociados.filter(
                            LineStatus__in=['A', 'L']
                        ).exists()

                        if not detalles_pendientes:
                            solicitud.TipoDoc = 'OC'
                        else:
                            solicitud.TipoDoc = 'SOL'
                        solicitud.save()

                        return JsonResponse({'message': 'Servicio enviado y guardado correctamente.'}, status=200)

                    except Exception as e:
                        # Si algo falla durante la actualización de la BD, hacer rollback
                        transaction.set_rollback(True)
                        raise Exception(f"Error al actualizar la base de datos: {str(e)}")
            else:
                return JsonResponse({
                    'error': f"Error en SAP: {response.get('error', 'Error desconocido')}"
                }, status=response.get('status_code', 500))

        except Exception as e:
            print("Error completo en export_data_as_jsonServicios:")
            traceback.print_exc()
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Método no permitido'}, status=405)


def data_sender_servicios(json_data, solicitud):
    url_session = "https://CFR-I7-1:50000/b1s/v1/Login"
    payload_session = json.dumps({
        "CompanyDB": "BDPRUEBASOCL",
        "Password": "m1r1",
        "UserName": "manager"
    })
    headers_session = {
        'Content-Type': 'application/json',
    }

    session = requests.Session()
    session.verify = False  # Desactivar verificación SSL

    # Configurar timeouts más largos
    session.timeout = (30, 60)  # (connect timeout, read timeout)

    for attempt in range(5):
        try:
            print(f"\nIntento {attempt + 1} de inicio de sesión...")
            
            # Esperar más tiempo entre intentos
            if attempt > 0:
                wait_time = attempt * 3
                print(f"Esperando {wait_time} segundos antes del siguiente intento...")
                time.sleep(wait_time)

            response_session = session.post(url_session, headers=headers_session, data=payload_session)

            if response_session.status_code == 200:
                session_cookie = response_session.cookies.get('B1SESSION')
                route_id_cookie = response_session.cookies.get('ROUTEID', '.node1')  # Valor por defecto

                if not session_cookie:
                    print("No se obtuvo B1SESSION, reintentando...")
                    continue

                cookie_string = f'B1SESSION={session_cookie}; ROUTEID={route_id_cookie}'
                print(f"Sesión iniciada - B1SESSION: {session_cookie}, ROUTEID: {route_id_cookie}")

                # Intentar la creación de la orden de compra
                url = "https://CFR-I7-1:50000/b1s/v1/PurchaseOrders"
                headers = {
                    'Content-Type': 'application/json',
                    'Cookie': cookie_string
                }

                try:
                    print("Enviando orden de servicio a SAP...")
                    print(f"JSON a enviar: {json_data}")
                    
                    for purchase_attempt in range(3):  # Intentos específicos para PurchaseOrders
                        try:
                            response = session.post(
                                url, 
                                headers=headers, 
                                data=json_data,
                                timeout=(30, 90)  # Aumentar timeout para esta llamada específica
                            )

                            if response.status_code == 201:
                                try:
                                    response_json = response.json()
                                    doc_entry = response_json.get('DocEntry')
                                    print(f"Orden de servicio creada exitosamente. DocEntry: {doc_entry}")
                                    return {
                                        'status': 'success',
                                        'doc_entry': doc_entry
                                    }
                                except json.JSONDecodeError as e:
                                    print(f"Error decodificando respuesta JSON: {str(e)}")
                                    if purchase_attempt < 2:
                                        print("Reintentando envío de orden...")
                                        time.sleep(3)
                                        continue
                            else:
                                try:
                                    error_json = response.json()
                                    error_message = error_json.get('error', {}).get('message', {}).get('value', 'Error desconocido')
                                except json.JSONDecodeError:
                                    error_message = response.text

                                print(f"Error en respuesta SAP: Status {response.status_code} - {error_message}")
                                if purchase_attempt < 2:
                                    print("Reintentando envío de orden...")
                                    time.sleep(3)
                                    continue

                                return {
                                    'status': 'error',
                                    'error': error_message,
                                    'status_code': response.status_code
                                }

                        except requests.exceptions.RequestException as e:
                            print(f"Error en intento {purchase_attempt + 1} de envío de orden: {str(e)}")
                            if purchase_attempt < 2:
                                print("Reintentando envío de orden...")
                                time.sleep(3)
                                continue
                            if attempt < 4:  # Si aún quedan intentos de sesión
                                raise  # Forzar reintento de sesión completa

                    # Si llegamos aquí, fallaron todos los intentos de PurchaseOrders
                    if attempt < 4:  # Si aún quedan intentos de sesión
                        continue  # Intentar nueva sesión
                    return {
                        'status': 'error',
                        'error': 'Falló el envío de la orden después de múltiples intentos',
                        'status_code': 500
                    }

                except Exception as e:
                    print(f"Error inesperado: {str(e)}")
                    if attempt < 4:
                        continue
                    return {
                        'status': 'error',
                        'error': str(e),
                        'status_code': 500
                    }

            else:
                print(f"Error en inicio de sesión: {response_session.status_code} - {response_session.text}")
                if attempt == 4:
                    return {
                        'status': 'error',
                        'error': f"Error al iniciar sesión después de 5 intentos: {response_session.status_code}",
                        'status_code': 500
                    }

        except Exception as e:
            print(f"Error en intento {attempt + 1}: {str(e)}")
            if attempt == 4:
                return {
                    'status': 'error',
                    'error': str(e),
                    'status_code': 500
                }
            time.sleep(2)

    return {
        'status': 'error',
        'error': 'No se pudo completar la operación después de 5 intentos',
        'status_code': 500
    }


def guardar_orden_compra_oc_servicio(detalles_seleccionados, solicitud, tipo, proveedor, request):
    try:
        # Buscar el proveedor en la base de datos
        proveedor_instance = OCRD.objects.get(CardCode=proveedor)
    except OCRD.DoesNotExist:
        raise Exception(f'El proveedor con código {proveedor} no existe.')

    # Obtener la serie de OrdenCompra y el siguiente número
    serie_instance = Series.objects.get(Nombre='OrdenCompra')
    doc_num_oc = serie_instance.NumeroSiguiente

    # Calcular el TotalOC sumando los totales de los detalles
    total_oc = sum(detalle.Precio * detalle.Quantity for detalle in detalles_seleccionados)

    # Determinar el TotalImpuestosOC
    if solicitud.TaxCode.Code == "IGV":
        total_impuestos_oc = total_oc * 0.18
    else:
        total_impuestos_oc = solicitud.TotalImp

    # Crear la cabecera de la orden de compra
    orden_compra_cabecera = OCC.objects.create(
        DocNumOC=doc_num_oc,
        SerieOC=serie_instance,
        SolicitanteOC=solicitud.ReqIdUser,
        DocTypeOC=tipo,
        DocDateOC=solicitud.DocDate,
        DocDueDateOC=solicitud.DocDueDate,
        SystemDateOC=date.today(),
        ProveedorOC=proveedor_instance,
        MonedaOC=solicitud.moneda,
        TaxCodeOC=solicitud.TaxCode,
        TotalOC=total_oc,
        TotalImpuestosOC=total_impuestos_oc + total_oc,
        CommentsOC=solicitud.Comments,
    )

    # Crear los detalles en OCD1
    current_time = timezone.now()
    for detalle in detalles_seleccionados:
        # Actualizar PRQ1 con datos de logística
        detalle.idLogistica = request.user
        detalle.DateLogistica = current_time
        detalle.save()

        # Crear el detalle en OCD1 con todos los IDs y fechas
        OCD1.objects.create(
            NumDocOCD=orden_compra_cabecera,
            ItemCodeOCD=detalle.ItemCode,
            LineVendorOCD=proveedor_instance,
            DescriptionOCD=detalle.Description,
            QuantityOCD=detalle.Quantity,
            UnidadMedidaOCD=detalle.UnidadMedida,
            AlmacenOCD=detalle.Almacen,
            CuentaMayorOCD=detalle.CuentaMayor,
            PrecioOCD=detalle.Precio,
            TotalOCD=detalle.Precio * detalle.Quantity,
            LineStatusOCD='C',
            DimensionOCD=detalle.idDimension,
            DocNumSAPOCD=None,
            BaseEntryOCD=detalle.NumDoc.DocNumSAP,
            BaseLineOCD=detalle.LineCount_Indexado,
            DocEntryOCD=detalle.NumDoc.DocEntry,
            # Agregar los tres IDs y fechas
            idAreaGeneralOCD=detalle.idAreaGeneral,
            DateAreaGeneralOCD=detalle.DateAreaGeneral,
            idJefePresupuestosOCD=detalle.idJefePresupuestos,
            DateJefePresupuestosOCD=detalle.DateJefePresupuestos,
            idLogisticaOCD=request.user,
            DateLogisticaOCD=current_time
        )

    # Incrementar el NumeroSiguiente en la serie
    serie_instance.NumeroSiguiente += 1
    serie_instance.save()

    return orden_compra_cabecera



# # LISTA DE ORDENES
# class OrdenCompraListView(ValidatePermissionRequiredMixin2, ListView):
#     model = OCC
#     template_name = 'OrdenCompra/listar_orden_compra.html'
#     required_groups = ['Jefe_Logistica', 'Jefe_de_Presupuestos']
    
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['title'] = 'Listado de Órdenes de Compra'
#         context['entity'] = 'Ordenes de Compra'
#         return context

#     @method_decorator(csrf_exempt)
#     def dispatch(self, request, *args, **kwargs):
#         return super().dispatch(request, *args, **kwargs)

#     def get_queryset(self):
#         return OCC.objects.prefetch_related(
#             'detalles_oc',  # Asegúrate de que este es el related_name correcto
#             Prefetch(
#                 'detalles_oc__NumDocOCD',  # Este sería un ejemplo de cómo traer detalles de OPRQ asociados a OCD1
#                 queryset=OPRQ.objects.prefetch_related(
#                     'detalles_prq1'  # Aquí traes los detalles de PRQ1 asociados a OPRQ
#                 )
#             )
#         )

#     def post(self, request, *args, **kwargs):
#         data = {}
#         try:
#             action = request.POST['action']
#             if action == "searchdata":
#                 data = {
#                     'data': [],
#                     'draw': request.POST.get('draw', 1),
#                     'recordsTotal': OCC.objects.count(),
#                     'recordsFiltered': OCC.objects.count()
#                 }
                
#                 position = 1  # Initialize position counter
#                 for orden in self.get_queryset():
#                     item = orden.toJSON()
#                     item['position'] = position  # Add position to item
#                     detalles = []
#                     for detalle in orden.detalles_oc.all():
#                         detalle_dict = detalle.toJSON()  # Asegúrate de que detalle también tenga un método toJSON
#                         detalles.append(detalle_dict)
#                     item['detalles'] = detalles
#                     item['origins'] = []
#                     for detalle in orden.detalles_oc.all():
#                         item['origins'].append({
#                             'BaseEntryOCD': detalle.BaseEntryOCD,
#                             'DescriptionOCD': detalle.DescriptionOCD,
#                         })
#                     data['data'].append(item)
#                     position += 1  # Increment position counter
#         except Exception as e:
#             data = {'error': str(e)}
#         return JsonResponse(data, safe=False)

class OrdenCompraListView(ValidatePermissionRequiredMixin2, ListView):
    model = OCC
    template_name = 'OrdenCompra/listar_orden_compra.html'
    required_groups = ['Jefe_Logistica', 'Jefe_de_Presupuestos']
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Listado de Órdenes de Compra'
        context['entity'] = 'Ordenes de Compra'
        return context

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return OCC.objects.prefetch_related(
            'detalles_oc',
            Prefetch(
                'detalles_oc__NumDocOCD',
                queryset=OPRQ.objects.prefetch_related(
                    'detalles_prq1'
                )
            )
        ).order_by('-DocNumOC')

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == "searchdata":
                data = {
                    'data': [],
                    'draw': request.POST.get('draw', 1),
                    'recordsTotal': OCC.objects.count(),
                    'recordsFiltered': OCC.objects.count()
                }
                
                for orden in self.get_queryset():
                    item = orden.toJSON()
                    detalles = []
                    for detalle in orden.detalles_oc.all():
                        detalle_dict = detalle.toJSON()
                        detalles.append(detalle_dict)
                    item['detalles'] = detalles
                    item['origins'] = []
                    for detalle in orden.detalles_oc.all():
                        origen_info = {
                            'BaseEntryOCD': detalle.BaseEntryOCD,
                            'DescriptionOCD': detalle.DescriptionOCD,
                            'idAreaGeneralOCD': {
                                'username': str(detalle.idAreaGeneralOCD) if detalle.idAreaGeneralOCD else None,
                                'full_name': detalle.idAreaGeneralOCD.first_name if detalle.idAreaGeneralOCD else None
                            },
                            'DateAreaGeneralOCD': detalle.DateAreaGeneralOCD.strftime('%Y-%m-%d %H:%M:%S') if detalle.DateAreaGeneralOCD else None,
                            'idJefePresupuestosOCD': {
                                'username': str(detalle.idJefePresupuestosOCD) if detalle.idJefePresupuestosOCD else None,
                                'full_name': detalle.idJefePresupuestosOCD.first_name if detalle.idJefePresupuestosOCD else None
                            },
                            'DateJefePresupuestosOCD': detalle.DateJefePresupuestosOCD.strftime('%Y-%m-%d %H:%M:%S') if detalle.DateJefePresupuestosOCD else None,
                            'idLogisticaOCD': {
                                'username': str(detalle.idLogisticaOCD) if detalle.idLogisticaOCD else None,
                                'full_name': detalle.idLogisticaOCD.first_name if detalle.idLogisticaOCD else None
                            },
                            'DateLogisticaOCD': detalle.DateLogisticaOCD.strftime('%Y-%m-%d %H:%M:%S') if detalle.DateLogisticaOCD else None,
                        }
                        item['origins'].append(origen_info)
                    data['data'].append(item)
        except Exception as e:
            data = {'error': str(e)}
        return JsonResponse(data, safe=False)

#DETALLES DE ORDEN
@csrf_exempt
def get_solicitud_detalle(request, base_entry):
    try:
        # Limpiar el base_entry de espacios y "Ver"
        base_entry_clean = base_entry.split()[0]
        solicitud = OPRQ.objects.get(DocNumSAP=base_entry_clean)
        return JsonResponse(solicitud.toJSON())
    except OPRQ.DoesNotExist:
        return JsonResponse({'error': f'Solicitud con BaseEntry {base_entry_clean} no encontrada'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
#DETALLES DE TABLA PRODUCTO DENTRO DE OC
@csrf_exempt
def get_solicitud_detalle_producto(request, doc_num):
    try:
        print(f"Buscando DocEntry en OPRQ para DocNum: {doc_num}")
        # First get DocEntry from OPRQ
        oprq = OPRQ.objects.get(DocNum=doc_num)
        print(f"DocEntry encontrado: {oprq.DocEntry}")
        
        # Then use DocEntry to query PRQ1
        detalles = PRQ1.objects.filter(
            NumDoc_id=oprq.DocEntry
        ).select_related(
            'ItemCode',
            'LineVendor',
            'UnidadMedida',
            'Almacen'
        ).values(
            'ItemCode__ItemCode',
            'LineVendor__CardName',
            'Description',
            'Quantity',
            'Precio',
            'UnidadMedida__Name',
            'Almacen__WhsName',
            'total',
            'LineStatus',
            'Quantity_rest',
        )
        print(f"Detalles encontrados: {detalles.count()}")
        return JsonResponse(list(detalles), safe=False)
    except OPRQ.DoesNotExist:
        print(f"No se encontró OPRQ con DocNum: {doc_num}")
        return JsonResponse([], safe=False)
    except Exception as e:
        print(f"Error: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)
    
#DETALLES DE TABLA SERVICIO DENTRO DE OC
@csrf_exempt
def get_solicitud_detalle_servicio(request, doc_num):
    try:
        print(f"Buscando DocEntry en OPRQ para DocNum: {doc_num}")
        # Get DocEntry from OPRQ
        oprq = OPRQ.objects.get(DocNum=doc_num)
        print(f"DocEntry encontrado: {oprq.DocEntry}")
        
        # Query PRQ1 using DocEntry
        detalles = PRQ1.objects.filter(
            NumDoc_id=oprq.DocEntry
        ).select_related(
            'ItemCode',
            'LineVendor',
            'CuentaMayor'
        ).values(
            'ItemCode__ItemCode',
            'LineVendor__CardName',
            'Description',
            'Quantity',
            'Precio',
            'CuentaMayor__AcctName',
            'total',
            'LineStatus'
        )
        print(f"Servicios encontrados: {detalles.count()}")
        return JsonResponse(list(detalles), safe=False)
    except OPRQ.DoesNotExist:
        print(f"No se encontró OPRQ con DocNum: {doc_num}")
        return JsonResponse([], safe=False)
    except Exception as e:
        print(f"Error: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)
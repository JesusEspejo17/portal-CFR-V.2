from typing import Any
import json
import requests
from django.http import HttpRequest
from django.http.response import HttpResponse as HttpResponse
from django.shortcuts import render, redirect
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
from django.db.models import Prefetch


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
def solicitudcompra(request):
    template_name = 'SolicitudCompra/create_solicitud_compra.html'
    fecha = datetime.today().strftime('%d-%m-%Y')
    success_url = reverse_lazy('erp:listar_solicitudes')
    if request.method=='GET':
        coin = Moneda.objects.filter()
        impuestos = OSTA.objects.filter()
        departamento = Departamento.objects.filter()
        serie = Series.objects.filter()

        cuentaContable=OACT.objects.exclude(AcctName__icontains='Sin Cuenta Contable')
        cuentaContable_json = json.dumps(list(cuentaContable.values('AcctCode', 'AcctName')))

        socioNegocio=OCRD.objects.filter()
        socioNegocio_json = json.dumps(list(socioNegocio.values('CardCode', 'CardName')))

        medida = OUOM.objects.exclude(Name__icontains='Sin Unidad')
        medida_json = json.dumps(list(medida.values('Code', 'Name')))

        almacen=OWHS.objects.exclude(WhsName__icontains='Sin Almacen')
        almacenes_json = json.dumps(list(almacen.values('WhsCode', 'WhsName')))

        dimension = Dimensiones.objects.filter()
        dimension_json = json.dumps(list(dimension.values('nombre', 'descripcion')))
        

        grupo_especifico = Group.objects.get(name='Administrador')
        pertenece_al_grupo = request.user.groups.filter(name=grupo_especifico).exists()
        contexto={'moneda': coin, 
                  'OSTA':impuestos, 
                  'title':' Nueva Solicitud de Compra',
                  'fecha': fecha,
                  'serie': serie,
                  'Departamento':departamento,
                  'cuenta_contable':cuentaContable_json,
                  'socio_negocio':socioNegocio_json,
                  'almacen': almacenes_json,
                  'medida': medida_json,
                  'dimension': dimension_json
                  }
        return render(request, template_name, contexto)
    if request.method=='POST':
        try:
            with transaction.atomic():
                NombreSerie = request.POST.get('serie')
                serie = Series.objects.get(Nombre=NombreSerie)
                if(serie.NumeroSiguiente>serie.UltimoNumero):
                    msg = "ERROR: Se ha llegado al límite de solicitudes de compra guardadas por el sistema para esa serie."
                    render(request, template_name, {'error message': msg})
                
                #Cargamos vents para los productos

                vents_data = request.POST.get('vents_data', '{}')
                servs_data = request.POST.get('servs_data', '{}')
                
                # print("Datos de vents recibidos:", vents_data) 
                # print("Datos de servs recibidos:", servs_data) 

                # Procesa los datos JSON de vents_data y servs_data como necesites
                vents = json.loads(vents_data)
                servs = json.loads(servs_data)
                
                if not vents and not servs:
                    msg = "ERROR: No se ha ingresado ningún producto o servicio."
                    return render(request, template_name, {'error_message': msg})
                
                #Inicialización de datos necesarios
                encabezado = OPRQ()
                #User
                nameUser = request.POST.get('idUser') 
                usuario = User()
                usuario = User.objects.get(id=nameUser)

                #Impuestos
                imp = request.POST.get('TaxCode') 
                cadImpuesto = imp.split('-',1)  #imp está en el formato "Nombre - Codigo"
                code_Impuesto = cadImpuesto[-1].strip()
                impuesto = OSTA.objects.get(Code=code_Impuesto)

                #Moneda
                abreviacionMoneda = request.POST.get('moneda') 
                moneda = Moneda.objects.get(MonedaAbrev=abreviacionMoneda)

                #Departamento
                deptName = request.POST.get('Department')
                departamento = Departamento.objects.get(Name=deptName)

                #Save encabezado
                encabezado.DocNum = request.POST.get('DocNum')
                encabezado.ReqIdUser = usuario
                encabezado.ReqCode = usuario.SAP_Code
                encabezado.ReqType = usuario.UserType
                encabezado.Department = departamento
                encabezado.Serie = serie.CodigoSerie
                encabezado.DocStatus = "P" #P: pendiente, A: aprobado, R: rechazado C:contabilizado
                #Si el arreglo de servicios está vacío, se está agregando un producto
                if (servs == [] and len(vents) > 0):
                    encabezado.DocType = "I"
                #Si el arreglo de productos está vacío, se está agregando un servicio
                elif(vents == [] and len(servs) > 0):
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
                #Save detalle
                #Si el arreglo de servicios está vacío, se está agregando un producto
                if (servs == [] and len(vents) > 0):
                    for i in vents:
                        detalle = PRQ1()
                        item = OITM.objects.get(ItemCode=i['code'])
                        proveedor = OCRD.objects.get(CardName=i['proveedor'])
                        uni_med = OUOM.objects.get(Code=i['medida'])
                        almacen = OWHS.objects.get(WhsName=i['almacen'])
                        cuentaContable = OACT.objects.get(AcctName="Sin Cuenta Contable")
                        dimension = Dimensiones.objects.get(descripcion=i['dimension'])
                        detalle.NumDoc = encabezado
                        detalle.ItemCode = item
                        detalle.LineVendor = proveedor
                        detalle.Description = i['description']
                        detalle.Quantity = i['cant']
                        detalle.UnidadMedida = uni_med
                        detalle.Currency = moneda
                        detalle.Almacen = almacen
                        detalle.CuentaMayor = cuentaContable
                        detalle.total = i['precio_total']
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
                #Si el arreglo de productos está vacío, se está agregando un servicio
                elif(vents == [] and len(servs) > 0):
                    for i in servs:
                        detalle = PRQ1()
                        item = OITM.objects.get(ItemCode=i['code'])
                        proveedor = OCRD.objects.get(CardName=i['proveedor'])
                        cuentaContable = OACT.objects.get(AcctName=i['cuenta_contable'])
                        uni_med = OUOM.objects.get(Code="Sin Unidad")
                        almacen = OWHS.objects.get(WhsName="Sin Almacen")
                        dimension = Dimensiones.objects.get(descripcion=i['dimension'])
                        detalle.NumDoc = encabezado
                        detalle.ItemCode = item
                        detalle.LineVendor = proveedor
                        detalle.Description = i['description']
                        detalle.Quantity = i['cant']
                        detalle.UnidadMedida = uni_med
                        detalle.Currency = moneda
                        detalle.Almacen = almacen
                        detalle.CuentaMayor = cuentaContable
                        detalle.total = i['precio_total']
                        if 'price' in i:
                            try:
                                detalle.Precio = float(i['price'])
                                print("Precio asignado:", detalle.Precio)
                            except ValueError:
                                detalle.Precio = 0.0  # O manejar de otra manera
                        else:
                            detalle.Precio = 0.0
                            print("Advertencia: 'precio' no encontrado en item:", i)
                        detalle.idDimension = dimension
                        detalle.save()
                #Actualizar modelo Series
                if serie:
                    serie.NumeroSiguiente +=1
                    serie.save()
                success_message = "La solicitud de compra se ha guardado correctamente."
                send_email_to_validator()
                return render(request, template_name, {'success_message': success_message})
                                                    
        except Exception as e:
            msg = f"Error al insertar datos maestros: {str(e)}"  # Corregido
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

# class ListSolicitudesCompra(ValidatePermissionRequiredMixin2, ListView):
#     model: OPRQ
#     template_name = 'SolicitudCompra/listar_solicitud_compra.html'
#     required_groups = ['Empleado', 'Validador', 'Jefe_De_Area', 'Jefe_de_Presupuestos']
#     @method_decorator(csrf_exempt)
#     def dispatch(self, request, *args, **kwargs):
#         return super().dispatch(request, *args, **kwargs)
#     def post(self, request, *args, **kwargs):
#         data = {}
#         try:
#             action = request.POST['action']
#             if action == "searchSolicitudes":
#                 estado = request.POST['estado']
#                 data = []
#                 user = self.request.user
#                 if user.groups.filter(name__in=['Administrador', 'Validador']).exists():
#                     if estado == '0':
#                         solicitudes = OPRQ.objects.order_by('DocEntry')
#                     else:
#                         solicitudes = OPRQ.objects.filter(DocStatus=estado).order_by('DocEntry')
#                 elif user.groups.filter(name__in=['Jefe_De_Area']).exists():
#                     depto = Departamento.objects.get(Name=user.departamento)
#                     if estado == '0':
#                         solicitudes = OPRQ.objects.filter(Department=depto.Code).order_by('DocEntry')
#                     else:
#                         solicitudes = OPRQ.objects.filter(DocStatus=estado).filter(Department=depto.Code).order_by('DocEntry')
#                 elif user.groups.filter(name__in=['Empleado']).exists():
#                     if estado == '0':
#                         solicitudes = OPRQ.objects.filter(ReqIdUser=user.id).order_by('DocEntry')
#                     else:
#                         solicitudes = OPRQ.objects.filter(ReqIdUser=user.id).filter(DocStatus=estado).order_by('DocEntry')
#                 elif user.groups.filter(name__in=['Jefe_de_Presupuestos']).exists():
#                     solicitudes = OPRQ.objects.filter(DocStatus='A').order_by('DocEntry')          
#                 for i in solicitudes:
#                     data.append(i.toJSON())
#             elif action == "showDetails":
#                 data = []
#                 for i in PRQ1.objects.filter(NumDoc=request.POST['id']):
#                     data.append(i.toJSON())
#             elif action=="getDetails":
#                 data = []
#                 for i in PRQ1.objects.filter(NumDoc=request.POST['code']):
#                     data.append(i.toJSON())
#             else:
#                 data['error'] = 'Ha ocurrido un error'
#         except Exception as e:
#             data['error'] = {{str(e)}}
#         return JsonResponse(data, safe=False)

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['title'] = 'Listado de Solicitudes'
#         context['entity'] = 'OPRQ'
#         context['edition_permissions'] = self.request.user.has_perm('erp.change_oprq')
#         return context
    
#     def get_queryset(self):
#         return OPRQ.objects.order_by('DocNum')
    
# @login_required
# def get_user_groups(request):
#     if request.user.is_authenticated:
#         user_groups = list(request.user.groups.values_list('name', flat=True))
#         return JsonResponse(user_groups, safe=False)
#     else:
#         return JsonResponse({'error': 'User not authenticated'}, status=401)

##ULTIMO LIST ANTES DE MODIFICACION DE NO LISTARSE C
# class ListSolicitudesCompra(ValidatePermissionRequiredMixin2, ListView):
#     model = OPRQ
#     template_name = 'SolicitudCompra/listar_solicitud_compra.html'
#     required_groups = ['Empleado', 'Validador', 'Jefe_De_Area', 'Jefe_de_Presupuestos']

#     @method_decorator(csrf_exempt)
#     def dispatch(self, request, *args, **kwargs):
#         return super().dispatch(request, *args, **kwargs)

#     def post(self, request, *args, **kwargs):
#         data = {}
#         try:
#             action = request.POST['action']
#             if action == "searchSolicitudes":
#                 estado = request.POST['estado']
#                 data = []
#                 user = self.request.user
#                 if user.groups.filter(name__in=['Administrador', 'Validador']).exists():
#                     if estado == '0':
#                         solicitudes = OPRQ.objects.order_by('DocEntry')
#                     else:
#                         solicitudes = OPRQ.objects.filter(DocStatus=estado).order_by('DocEntry')
#                 elif user.groups.filter(name__in=['Jefe_De_Area']).exists():
#                     depto = Departamento.objects.get(Name=user.departamento)
#                     if estado == '0':
#                         solicitudes = OPRQ.objects.filter(Department=depto.Code).order_by('DocEntry')
#                     else:
#                         solicitudes = OPRQ.objects.filter(DocStatus=estado).filter(Department=depto.Code).order_by('DocEntry')
#                 elif user.groups.filter(name__in=['Empleado']).exists():
#                     if estado == '0':
#                         solicitudes = OPRQ.objects.filter(ReqIdUser=user.id).order_by('DocEntry')
#                     else:
#                         solicitudes = OPRQ.objects.filter(ReqIdUser=user.id).filter(DocStatus=estado).order_by('DocEntry')
#                 elif user.groups.filter(name__in=['Jefe_de_Presupuestos']).exists():
#                     solicitudes = OPRQ.objects.filter(DocStatus__in=['A', 'C', 'CP']).order_by('DocEntry')  # Filtrar por 'A', 'C', 'CP'
#                 for i in solicitudes:
#                     data.append(i.toJSON())
#             elif action == "showDetails":
#                 data = []
#                 user = self.request.user
#                 if user.groups.filter(name__in=['Jefe_de_Presupuestos']).exists():
#                     for i in PRQ1.objects.filter(NumDoc=request.POST['id'], LineStatus='A'):  # Filtrar por LineStatus 'A'
#                         data.append(i.toJSON())
#                 else:
#                     for i in PRQ1.objects.filter(NumDoc=request.POST['id']):
#                         data.append(i.toJSON())
#             elif action == "getDetails":
#                 data = []
#                 user = self.request.user
#                 if user.groups.filter(name__in=['Jefe_de_Presupuestos']).exists():
#                     for i in PRQ1.objects.filter(NumDoc=request.POST['code'], LineStatus='A'):  # Filtrar por LineStatus 'A'
#                         data.append(i.toJSON())
#                 else:
#                     for i in PRQ1.objects.filter(NumDoc=request.POST['code']):
#                         data.append(i.toJSON())
#             else:
#                 data['error'] = 'Ha ocurrido un error'
#         except Exception as e:
#             data['error'] = str(e)
#         return JsonResponse(data, safe=False)

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['title'] = 'Listado de Solicitudes'
#         context['entity'] = 'OPRQ'
#         context['edition_permissions'] = self.request.user.has_perm('erp.change_oprq')
#         return context

#     def get_queryset(self):
#         return OPRQ.objects.order_by('DocNum')

# @login_required
# def get_user_groups(request):
#     if request.user.is_authenticated:
#         user_groups = list(request.user.groups.values_list('name', flat=True))
#         return JsonResponse(user_groups, safe=False)
#     else:
#         return JsonResponse({'error': 'User not authenticated'}, status=401)

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

@login_required
def get_user_groups(request):
    if request.user.is_authenticated:
        user_groups = list(request.user.groups.values_list('name', flat=True))
        return JsonResponse(user_groups, safe=False)
    else:
        return JsonResponse({'error': 'User not authenticated'}, status=401)


    
# def solicitudContabilizar(request,id):
#     Solicitud = OPRQ.objects.filter(pk=id)
#     if request.method=="POST":
#         try:
#             if Solicitud:
#                 validate = Validaciones()
#                 Solicitud.update(DocStatus="C")
#                 data = json.loads(request.body)
#                 usuario = data.get('usuario', None)
#                 validate.codReqUser = usuario
#                 validate.codValidador = request.user.username
#                 validate.fecha = timezone.now()
#                 validate.estado = "Contabilizado"
#                 validate.save()
#                 send_email_to_user(1)
#                 return HttpResponse("OK")
#         except Exception as e:
#             msg = f"Error al insertar datos maestros: {str(e)}"
#             return JsonResponse({'error': msg}, status=500)
#     return JsonResponse({'error': 'Metodo no permitido'}, status=405)

##CONTABILIZAR FALTA FUNCION ACTUALIZAR A C
# def solicitudContabilizar(request, id):
#     if request.method == "POST":
#         try:
#             data = json.loads(request.body)
#             usuario = data.get('usuario', None)
#             items_contabilizados = data.get('arrcheckedProd', [])
            
#             if not items_contabilizados:
#                 return JsonResponse({'error': 'Debe seleccionar al menos un item para contabilizar'}, status=400)

#             solicitud = OPRQ.objects.filter(pk=id).first()
#             if not solicitud:
#                 return JsonResponse({'error': 'Solicitud no encontrada'}, status=404)

#             with transaction.atomic():
#                 # Actualizar items seleccionados a 'L'
#                 detalles = PRQ1.objects.filter(NumDoc=id, Code__in=items_contabilizados)
#                 detalles_actualizados = detalles.update(LineStatus='L')

#                 # Verificar si todos los detalles están en 'L'
#                 todos_contabilizados = not PRQ1.objects.filter(NumDoc=id).exclude(LineStatus='L').exists()
                
#                 if todos_contabilizados:
#                     OPRQ.objects.filter(pk=id).update(DocStatus="C")
#                 else:
#                     OPRQ.objects.filter(pk=id).update(DocStatus="CP")

#                 validate = Validaciones()
#                 validate.codReqUser = usuario
#                 validate.codValidador = request.user.username
#                 validate.fecha = timezone.now()
#                 validate.estado = "Contabilizado"
#                 validate.save()
                
#                 send_email_to_user(1)
#                 return HttpResponse("OK")

#         except Exception as e:
#             msg = f"Error al insertar datos maestros: {str(e)}"
#             return JsonResponse({'error': msg}, status=500)
            
#     return JsonResponse({'error': 'Método no permitido'}, status=405)

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
                # Actualizar items seleccionados a 'L'
                detalles = PRQ1.objects.filter(NumDoc=id, Code__in=items_contabilizados)
                detalles_actualizados = detalles.update(LineStatus='L')

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
                validate.fecha = timezone.now()
                validate.estado = "Contabilizado"
                validate.save()
                
                send_email_to_user(1)
                return HttpResponse("OK")

        except Exception as e:
            msg = f"Error al insertar datos maestros: {str(e)}"
            return JsonResponse({'error': msg}, status=500)
            
    return JsonResponse({'error': 'Método no permitido'}, status=405)

# def solicitudContabilizarMasivo(request):
#     if request.method == "POST":
#         try:
#             data = json.loads(request.body)
#             arrSolicitudes = data.get('ids', None)
#             if not arrSolicitudes:
#                 return JsonResponse({'error': 'No se recibieron IDs'}, status=400)
#             with transaction.atomic():
#                 for id in arrSolicitudes:
#                     solicitud_actual = OPRQ.objects.get(pk=id)
#                     Solicitud_object = OPRQ.objects.filter(pk=id)
#                     validate = Validaciones()
#                     Solicitud_object.update(DocStatus="C")
#                     usuario = solicitud_actual.ReqIdUser
#                     usuario_solicitante = User.objects.get(username=usuario)
#                     validate.codReqUser = usuario_solicitante.first_name + ' ' + usuario.last_name
#                     validate.codValidador = request.user.username
#                     validate.fecha = timezone.now()
#                     validate.estado = "Contabilizado"
#                     validate.save()
#             return HttpResponse("OK")
#         except Exception as e:
#             msg = f"Error al insertar datos maestros: {str(e)}"
#             return JsonResponse({'error': msg}, status=500)
#     return JsonResponse({'error': 'Metodo no permitido'}, status=405)

def solicitudContabilizarMasivo(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            arrSolicitudes = data.get('ids', None)
            if not arrSolicitudes:
                return JsonResponse({'error': 'No se recibieron IDs'}, status=400)
            with transaction.atomic():
                for id in arrSolicitudes:
                    solicitud_actual = OPRQ.objects.get(pk=id)
                    Solicitud_object = OPRQ.objects.filter(pk=id)
                    
                    # Actualizar items seleccionados a 'L'
                    detalles = PRQ1.objects.filter(NumDoc=id, LineStatus='A')
                    detalles_actualizados = detalles.update(LineStatus='L')

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
                    validate.fecha = timezone.now()
                    validate.estado = "Contabilizado"
                    validate.save()
            return HttpResponse("OK")
        except Exception as e:
            msg = f"Error al insertar datos maestros: {str(e)}"
            return JsonResponse({'error': msg}, status=500)
    return JsonResponse({'error': 'Metodo no permitido'}, status=405)
    

# def solicitudAprobarMasivo(request):
#     if request.method == "POST":
#         try:
#             data = json.loads(request.body)
#             arrSolicitudes = data.get('ids', None)
#             checked_prod = data.get('arrcheckedProd', [])
#             if not arrSolicitudes:
#                 return JsonResponse({'error': 'No se recibieron IDs'}, status=400)
#             with transaction.atomic():
#                 for id in arrSolicitudes:
#                     Solicitud = OPRQ.objects.filter(pk=id)
#                     if not Solicitud:
#                         return JsonResponse({'error': 'Solicitud no encontrada'}, status=404)
#                     with transaction.atomic():
#                         detalles = PRQ1.objects.filter(NumDoc=id)
#                         if detalles.exists():
#                             original_status = {detalle.pk: detalle.LineStatus for detalle in detalles}
#                             checked_codes = {item.get('Code') for item in checked_prod}
#                         else:
#                             return JsonResponse({'error': 'Detalle no encontrado'}, status=404)
#                         for detalle in detalles:
#                             if detalle.Code in checked_codes:
#                                 if detalle.LineStatus != 'A':
#                                     detalle.LineStatus = 'A'
#                                     detalle.save()
#                             else:
#                                 if detalle.LineStatus != 'R':
#                                     detalle.LineStatus = 'R'
#                                     detalle.save()
#                     response = export_data_as_json(id)
#                     response_content = json.loads(response.content)
#                     error_message = response_content.get('error', 'Error desconocido')
#                     if response.status_code != 200:
#                         for detalle in detalles:
#                             detalle.LineStatus = original_status.get(detalle.pk, detalle.LineStatus)
#                             detalle.save()
#                         return JsonResponse({'error': error_message}, status=response.status_code)
#                     else:
#                         solicitud_actual = OPRQ.objects.get(pk=id)
#                         Solicitud_object = OPRQ.objects.filter(pk=id)
#                         validate = Validaciones()
#                         Solicitud_object.update(DocStatus="A")
#                         usuario = solicitud_actual.ReqIdUser
#                         usuario_solicitante = User.objects.get(username=usuario)
#                         validate.codReqUser = usuario_solicitante.first_name + ' ' + usuario.last_name
#                         validate.codValidador = request.user.username
#                         validate.fecha = timezone.now()
#                         validate.estado = "Aprobado"
#                         validate.save()
#             return JsonResponse({'success': "Éxito"}, status=200)
#         except Exception as e:
#             msg = f"Error al insertar datos maestros: {str(e)}"
#             return JsonResponse({'error': msg}, status=500)

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

                    # 1. Actualizar LineStatus de los detalles
                    for detalle in detalles:
                        if detalle.Code in checked_codes:
                            if detalle.LineStatus != 'A':
                                detalle.LineStatus = 'A'
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
                        validate.fecha = timezone.now()
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
                    Solicitud = OPRQ.objects.filter(pk=id)
                    if not Solicitud:
                        return JsonResponse({'error': 'Solicitud no encontrada'}, status=404)
                    with transaction.atomic():
                        detalles = PRQ1.objects.filter(NumDoc=id)
                        if detalles.exists():
                            for detalle in detalles:
                                detalle.LineStatus = 'R'
                                detalle.save()
                        else:
                            return JsonResponse({'error': 'Detalle no encontrado'}, status=404)
                    solicitud_actual = OPRQ.objects.get(pk=id)
                    Solicitud_object = OPRQ.objects.filter(pk=id)
                    validate = Validaciones()
                    Solicitud_object.update(DocStatus="R")
                    usuario = solicitud_actual.ReqIdUser
                    usuario_solicitante = User.objects.get(username=usuario)
                    validate.codReqUser = usuario_solicitante.first_name + ' ' + usuario.last_name
                    validate.codValidador = request.user.username
                    validate.fecha = timezone.now()
                    validate.estado = "Rechazado"
                    validate.save()
            return HttpResponse("OK")
        except Exception as e:
            msg = f"Error al insertar datos maestros: {str(e)}"
            return JsonResponse({'error': msg}, status=500)
    return JsonResponse({'error': 'Metodo no permitido'}, status=405)

#CODIGO ORIGINAL
# def solicitudAprobar(request,id):
#     if request.method=="POST":
#         try:
#             data = json.loads(request.body)
#             #print(f"Data recibida: {data}")
#             checked_prod = data.get('arrcheckedProd', [])
#             usuario = data.get('usuario', None)
#             Solicitud = OPRQ.objects.filter(pk=id)
#             if not Solicitud:
#                 return JsonResponse({'error': 'Solicitud no encontrada'}, status=404)
#             with transaction.atomic():
#                 detalles = PRQ1.objects.filter(NumDoc=id)
#                 if detalles.exists():
#                     original_status = {detalle.pk: detalle.LineStatus for detalle in detalles}
#                     checked_codes = {item.get('Code') for item in checked_prod}
#                 else:
#                     return JsonResponse({'error': 'Detalle no encontrado'}, status=404)
#                 #print(f"Checked Codes: {checked_codes}")
#                 for detalle in detalles:
#                     if detalle.Code in checked_codes:
#                         if detalle.LineStatus != 'A':
#                             detalle.LineStatus = 'A'
#                             detalle.save()
#                     else:
#                         if detalle.LineStatus != 'R':
#                             detalle.LineStatus = 'R'
#                             detalle.save()
#                 response = export_data_as_json(id)
#                 response_content = json.loads(response.content)
#                 error_message = response_content.get('error', 'Error desconocido')
#                 if response.status_code != 200:
#                     for detalle in detalles:
#                         detalle.LineStatus = original_status.get(detalle.pk, detalle.LineStatus)
#                         detalle.save()
#                     return JsonResponse({'error': error_message}, status=response.status_code)
#                 else:
#                     validate = Validaciones()
#                     Solicitud.update(DocStatus="A")
#                     data = json.loads(request.body)
#                     validate.codReqUser = usuario
#                     validate.codValidador = request.user.username
#                     validate.fecha = timezone.now()
#                     validate.estado = "Aprobado"
#                     validate.save()
#                     send_email_to_user(1)
#                     return JsonResponse({'success': "Éxito"}, status=200)
#         except Exception as e:
#             msg = f"Error al insertar datos maestros: {str(e)}"
#             return JsonResponse({'error': msg}, status=500)
#     return JsonResponse({'error': 'Metodo no permitido'}, status=405)


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

                # 1. Actualizar LineStatus de los detalles
                for detalle in detalles:
                    if detalle.Code in checked_codes:
                        if detalle.LineStatus != 'A':
                            detalle.LineStatus = 'A'
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
                        detalle.save()
                    return JsonResponse({'error': error_message}, status=response.status_code)
                else:
                    validate = Validaciones()
                    Solicitud.update(DocStatus="A")
                    validate.codReqUser = usuario
                    validate.codValidador = request.user.username
                    validate.fecha = timezone.now()
                    validate.estado = "Aprobado"
                    validate.save()
                    send_email_to_user(1)
                    return JsonResponse({'success': "Éxito"}, status=200)

        except Exception as e:
            msg = f"Error al insertar datos maestros: {str(e)}"
            return JsonResponse({'error': msg}, status=500)
    
    return JsonResponse({'error': 'Método no permitido'}, status=405)


# def solicitudRechazar(request, id):
#     print("----- Inicio de solicitudRechazar -----")
#     if request.method == "POST":
#         try:
#             print(f"  Método: POST")
#             data = json.loads(request.body)
#             print(f"  Datos recibidos: {data}")
#             usuario = data.get('usuario', None)
#             print(f"  Usuario: {usuario}")

#             Solicitud = OPRQ.objects.filter(pk=id)
#             print(f"  Solicitud encontrada (pk={id}): {Solicitud.exists()}")
#             if not Solicitud:
#                 print(f"  ERROR: Solicitud no encontrada (pk={id})")
#                 return JsonResponse({'error': 'Solicitud no encontrada'}, status=404)

#             with transaction.atomic():
#                 detalles = PRQ1.objects.filter(NumDoc=id)
#                 print(f"  Detalles encontrados para la solicitud (NumDoc={id}): {detalles.count()}")
#                 if detalles.exists():
#                     for i, detalle in enumerate(detalles):
#                         print(f"    Detalle {i+1}:")
#                         print(f"      Code: {detalle.Code}")
#                         print(f"      LineStatus actual: {detalle.LineStatus}")
#                         detalle.LineStatus = 'R'
#                         detalle.save()
#                         print(f"      LineStatus actualizado a: 'R'")
#                 else:
#                     print(f"  ERROR: No se encontraron detalles para la solicitud (NumDoc={id})")
#                     return JsonResponse({'error': 'Detalle no encontrado'}, status=404)

#                 validate = Validaciones()
#                 Solicitud.update(DocStatus="R")
#                 print(f"  DocStatus de la solicitud actualizado a: 'R'")
                
#                 validate.codReqUser = usuario
#                 validate.codValidador = request.user.username
#                 validate.fecha = timezone.now()
#                 validate.estado = "Rechazado"
#                 validate.save()
#                 send_email_to_user(0)
#                 print("----- Fin de solicitudRechazar (éxito) -----")
#                 return HttpResponse("OK")
#         except Exception as e:
#             msg = f"Error al insertar datos maestros: {str(e)}"
#             print(f"  ERROR: {msg}")
#             return JsonResponse({'error': msg}, status=500)
#     else:
#         print("  Método no permitido (no es POST)")
#     print("----- Fin de solicitudRechazar (error) -----")
#     return JsonResponse({'error': 'Metodo no permitido'}, status=405)

#FUNCIONA CON INSOMNIA
# def solicitudRechazar(request, id):
#     if request.method == "POST":
#         try:
#             data = json.loads(request.body)
#             usuario = data.get('usuario', None)
#             items_rechazados = data.get('arrcheckedProd', [])
            
#             # Validar que haya items seleccionados
#             if not items_rechazados:
#                 return JsonResponse({'error': 'Debe seleccionar al menos un item para rechazar'}, status=400)

#             solicitud = OPRQ.objects.filter(pk=id).first()
#             if not solicitud:
#                 return JsonResponse({'error': 'Solicitud no encontrada'}, status=404)

#             with transaction.atomic():
#                 # Actualizar solo los items seleccionados
#                 detalles = PRQ1.objects.filter(NumDoc=id, Code__in=items_rechazados)
#                 detalles.update(LineStatus='R')

#                 # Verificar si quedan líneas pendientes
#                 lineas_pendientes = PRQ1.objects.filter(NumDoc=id, LineStatus='P').exists()
                
#                 # Actualizar DocStatus solo si no quedan líneas pendientes
#                 if not lineas_pendientes:
#                     OPRQ.objects.filter(pk=id).update(DocStatus="R")

#                 validate = Validaciones()
#                 validate.codReqUser = usuario
#                 validate.codValidador = request.user.username
#                 validate.fecha = timezone.now()
#                 validate.estado = "Rechazado"
#                 validate.save()
                
#                 send_email_to_user(0)
#                 return HttpResponse("OK")

#         except Exception as e:
#             msg = f"Error al insertar datos maestros: {str(e)}"
#             return JsonResponse({'error': msg}, status=500)
            
#     return JsonResponse({'error': 'Método no permitido'}, status=405)

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

                # Verificar líneas pendientes
                # lineas_pendientes = PRQ1.objects.filter(NumDoc=id, LineStatus='P').exists()
                lineas_pendientes = PRQ1.objects.filter(NumDoc=id, LineStatus__in=['P', 'A']).exists()
                
                if not lineas_pendientes:
                    OPRQ.objects.filter(pk=id).update(DocStatus="R")

                validate = Validaciones()
                validate.codReqUser  = usuario
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
            #print(f"Detalle Code: {det.Code}, LineStatus: {det.LineStatus}")
            if det.LineStatus=='A' and solicitud.DocType == 'I':
                detalle_list = {
                    'ItemCode': det.ItemCode.ItemCode,
                    'LineVendor': det.LineVendor.CardCode,
                    "TaxCode": solicitud.TaxCode.Code,
                    'Quantity': det.Quantity,
                    "UnitPrice":det.Precio,
                    'CostingCode': det.idDimension.descripcion if det.idDimension else 'null',
                    'Currency': det.Currency.MonedaAbrev if det.Currency else 'null'
                }
                oprq['DocumentLines'].append(detalle_list)
            elif det.LineStatus=='A' and solicitud.DocType == 'S' :
                detalle_list = {
                ##  'ItemCode': det.ItemCode.ItemCode,
                    "ItemDescription":  det.ItemCode.ItemCode,
                    'LineVendor': det.LineVendor.CardCode,
                    "RequiredDate": solicitud.ReqDate,
                    "TaxCode": solicitud.TaxCode.Code,
                    'Quantity': det.Quantity,
                    "Price":det.Precio,
                    "UnitPrice":det.Precio,
                    "DocTotalFC":det.Precio*det.Quantity,
                    "AccountCode": det.CuentaMayor.AcctCode,
                    'CostingCode': det.idDimension.descripcion if det.idDimension else 'null',
                    'Currency': det.Currency.MonedaAbrev if det.Currency else 'null'
                }
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

# INGRESO A SAP EN LOGISTICA
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
                'NumDoc', 'ItemCode', 'Currency', 'UnidadMedida', 'Almacen', 'CuentaMayor', 'idDimension', 'NumDoc__moneda', 'NumDoc__TaxCode'
            )

            if not detalles:
                return JsonResponse({'error': 'No se encontraron detalles para los códigos proporcionados.'}, status=400)

            solicitud = detalles.first().NumDoc

            # Guardar orden de compra en OCC y OCD1
            orden_compra_cabecera = guardar_orden_compra_oc(detalles, solicitud, tipo='I', proveedor=proveedor)

            # Generar JSON para SAP
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
                oprq["DocumentLines"].append({
                    "LineNum": idx,
                    "ItemCode": detalle.ItemCode.ItemCode,
                    "ItemDescription": detalle.Description,
                    "Quantity": detalle.Quantity,
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
            response = data_sender_productos(json_data, solicitud)

            if response.get('status') == 'success':
                # Actualizar `DocNumSAPOC` en la cabecera
                doc_entry_sap = response.get('doc_entry')
                orden_compra_cabecera.DocNumSAPOC = doc_entry_sap
                orden_compra_cabecera.save()

                # Actualizar `DocNumSAPOCD` en los detalles
                detalles_ocd1 = OCD1.objects.filter(NumDocOCD=orden_compra_cabecera)
                for detalle_ocd1 in detalles_ocd1:
                    detalle_ocd1.DocNumSAPOCD = doc_entry_sap
                    detalle_ocd1.save()

                # Verificar si todos los detalles tienen LineStatus 'C' antes de cambiar TipoDoc
                detalles_asociados = PRQ1.objects.filter(NumDoc=solicitud.DocEntry)

                # Verificar si hay detalles pendientes con LineStatus 'A' o 'L'
                detalles_pendientes = detalles_asociados.filter(LineStatus__in=['A', 'L']).exists()

                if not detalles_pendientes:
                    # Solo actualizar tipo de documento a 'OC' si NO hay detalles pendientes
                    solicitud.TipoDoc = 'OC'
                else:
                    # Si hay detalles pendientes, mantener TipoDoc como 'SOL'
                    solicitud.TipoDoc = 'SOL'

                solicitud.save()
                return JsonResponse({'message': 'Producto enviado y guardado correctamente.'}, status=200)
            else:
                return JsonResponse({'error': response.get('error', 'Error al enviar a SAP')}, status=response.get('status_code', 500))
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Método no permitido'}, status=405)

def export_data_as_jsonServicios(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            items_data = data.get('items', [])
            proveedor_frontend = data.get('proveedor', None)

            if not items_data:
                return JsonResponse({'error': 'No se enviaron servicios.'}, status=400)

            items_codes = [item['Code'] for item in items_data]

            detalles = PRQ1.objects.filter(Code__in=items_codes).select_related(
                'NumDoc', 'ItemCode', 'Currency', 'CuentaMayor', 'idDimension', 'NumDoc__moneda', 'NumDoc__TaxCode', 'LineVendor'
            )

            if not detalles:
                return JsonResponse({'error': 'No se encontraron detalles para los códigos proporcionados.'}, status=400)

            solicitud = detalles.first().NumDoc

            # Determinar el proveedor
            if proveedor_frontend:
                proveedor = proveedor_frontend
            elif primera_detalle := detalles.first().LineVendor:
                proveedor = primera_detalle.CardCode
            else:
                return JsonResponse({'error': 'No se pudo determinar el proveedor para los servicios.'}, status=400)

            # Guardar orden de compra en OCC y OCD1
            orden_compra_cabecera = guardar_orden_compra_oc(detalles, solicitud, tipo='S', proveedor=proveedor)

            # Generar JSON para SAP
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
            response = data_sender_servicios(json_data, solicitud)
            print("JSON generado para Servicios para enviar:", json_data)

            if response.get('status') == 'success':
                # Actualizar `DocNumSAPOC` en la cabecera
                doc_entry_sap = response.get('doc_entry')
                orden_compra_cabecera.DocNumSAPOC = doc_entry_sap
                orden_compra_cabecera.save()

                # Actualizar `DocNumSAPOCD` en los detalles
                detalles_ocd1 = OCD1.objects.filter(NumDocOCD=orden_compra_cabecera)
                for detalle_ocd1 in detalles_ocd1:
                    detalle_ocd1.DocNumSAPOCD = doc_entry_sap
                    detalle_ocd1.save()

                # Verificar si todos los detalles tienen LineStatus 'C' antes de cambiar TipoDoc
                detalles_asociados = PRQ1.objects.filter(NumDoc=solicitud.DocEntry)

                # Verificar si hay detalles pendientes con LineStatus 'A' o 'L'
                detalles_pendientes = detalles_asociados.filter(LineStatus__in=['A', 'L']).exists()

                if not detalles_pendientes:
                    # Solo actualizar tipo de documento a 'OC' si NO hay detalles pendientes
                    solicitud.TipoDoc = 'OC'
                else:
                    # Si hay detalles pendientes, mantener TipoDoc como 'SOL'
                    solicitud.TipoDoc = 'SOL'

                solicitud.save()
                return JsonResponse({'message': 'Servicio enviado y guardado correctamente.'}, status=200)
            else:
                return JsonResponse({'error': response.get('error', 'Error al enviar a SAP')}, status=response.get('status_code', 500))

        except Exception as e:
            import traceback
            print("Error completo en export_data_as_jsonServicios:")
            traceback.print_exc()
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Método no permitido'}, status=405)


# DATA SENDER PARA CADA UNO - GEMINIS
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
                route_id_cookie = response_session.cookies.get('ROUTEID')
                cookie_string = f'B1SESSION={session_cookie}; ROUTEID={route_id_cookie}'
                print("Inicio de sesión exitoso!")
                print(f"Código de estado de la sesión: {response_session.status_code}")
                print(f"Cookies de sesión: {cookie_string}")
                break
            else:
                print(f"Intento {attempt + 1} fallido: Error en la solicitud de sesión: {response_session.status_code} - {response_session.text}")
                if attempt == 4:
                    return {'status': 'error', 'error': f"Error al iniciar sesión después de 5 intentos: {response_session.status_code}", 'status_code': 500}
                time.sleep(2)
        except requests.RequestException as e:
            print(f"Error en el intento {attempt + 1}: {str(e)}")
            if attempt == 4:
                return {'status': 'error', 'error': f"Error al intentar iniciar sesión después de 5 intentos: {str(e)}", 'status_code': 500}
            time.sleep(2)

    url = "https://CFR-I7-1:50000/b1s/v1/PurchaseOrders"
    headers = {
        'Content-Type': 'application/json',
        'Cookie': cookie_string
    }
    response = session.post(url, headers=headers, data=json_data, verify=False)

    if response.status_code == 201:
        try:
            response_json = response.json()
            print(f"Respuesta de SAP (Productos): {response_json}")
            
            doc_entry = response_json.get('DocEntry')
            print(f"DocEntry extraído (Productos): {doc_entry}")
            
            if doc_entry:
                return {'status': 'success', 'doc_entry': doc_entry} 
                ordenes_compra = Orden_Compra.objects.filter(NumDoc_id=solicitud.pk, DocNumSAPoc__isnull=True)
                print(f"Ordenes de compra encontradas para actualizar (Productos): {ordenes_compra}")
                for orden in ordenes_compra:
                    print(f"Actualizando Orden de Compra (Productos) NumDoc_id: {orden.NumDoc_id}, solicitud.pk: {solicitud.pk}, DocEntry: {doc_entry}")
                    orden.DocNumSAPoc = doc_entry
                    orden.save()
                return {'status': 'success'}
            else:
                return {'status': 'error', 'error': 'DocEntry no encontrado en la respuesta de SAP', 'status_code': 500}
        except json.JSONDecodeError:
            return {'status': 'error', 'error': f"Error al decodificar la respuesta de SAP: {response.text}", 'status_code': 500}
    else:
        try:
            response_dict = response.json()
            value_message = response_dict.get('error', {}).get('message', {}).get('value', 'Error desconocido')
        except json.JSONDecodeError:
            value_message = f"Error al decodificar la respuesta: {response.text}"
        error_message = f"Error en la solicitud de PurchaseOrders: {response.status_code} - {response.text}"
        print("Error completo en la solicitud:", error_message)
        return {'status': 'error', 'error': value_message, 'status_code': response.status_code}

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

    for attempt in range(5):
        try:
            response_session = session.post(url_session, headers=headers_session, data=payload_session, verify=False)

            if response_session.status_code == 200:
                session_cookie = response_session.cookies.get('B1SESSION')
                route_id_cookie = response_session.cookies.get('ROUTEID')
                cookie_string = f'B1SESSION={session_cookie}; ROUTEID={route_id_cookie}'
                print("Inicio de sesión exitoso!")
                print(f"Código de estado de la sesión: {response_session.status_code}")
                print(f"Cookies de sesión: {cookie_string}")
                break
            else:
                print(f"Intento {attempt + 1} fallido: Error en la solicitud de sesión: {response_session.status_code} - {response_session.text}")
                if attempt == 4:
                    return {'status': 'error', 'error': f"Error al iniciar sesión después de 5 intentos: {response_session.status_code}", 'status_code': 500}
                time.sleep(2)
        except requests.RequestException as e:
            print(f"Error en el intento {attempt + 1}: {str(e)}")
            if attempt == 4:
                return {'status': 'error', 'error': f"Error al intentar iniciar sesión después de 5 intentos: {str(e)}", 'status_code': 500}
            time.sleep(2)

    url = "https://CFR-I7-1:50000/b1s/v1/PurchaseOrders"
    headers = {
        'Content-Type': 'application/json',
        'Cookie': cookie_string
    }
    try:
        response = session.post(url, headers=headers, data=json_data, verify=False)

        if response.status_code == 201:
            try:
                response_json = response.json()
                print(f"Respuesta de SAP (Servicios): {response_json}")
                
                doc_entry = response_json.get('DocEntry')
                print(f"DocEntry extraído (Servicios): {doc_entry}")
                
                if doc_entry:
                   ordenes_compra = Orden_Compra.objects.filter(NumDoc_id=solicitud.pk, DocNumSAPoc__isnull=True)
                   print(f"Ordenes de compra encontradas para actualizar (Servicios): {ordenes_compra}")
                   
                   for orden in ordenes_compra:
                       print(f"Actualizando Orden de Compra (Servicios) NumDoc_id: {orden.NumDoc_id}, solicitud.pk: {solicitud.pk}, DocEntry: {doc_entry}")
                       
                       orden.DocNumSAPoc = doc_entry
                       orden.save()
                   return {'status': 'success', 'doc_entry': doc_entry} # Return doc_entry here
                else:
                    return {'status': 'error', 'error': 'DocEntry no encontrado en la respuesta de SAP', 'status_code': 500}
            except json.JSONDecodeError:
                return {'status': 'error', 'error': f"Error al decodificar la respuesta de SAP: {response.text}", 'status_code': 500}
        else:
            try:
                response_dict = response.json()
                value_message = response_dict.get('error', {}).get('message', {}).get('value', 'Error desconocido')
            except json.JSONDecodeError:
                value_message = f"Error al decodificar la respuesta: {response.text}"
            error_message = f"Error en la solicitud de PurchaseOrders: {response.status_code} - {response.text}"
            print("Error completo en la solicitud:", error_message)
            return {'status': 'error', 'error': value_message, 'status_code': response.status_code}

    except requests.RequestException as e:
        print(f"Error en la solicitud a PurchaseOrders: {str(e)}")
        return {'status': 'error', 'error': f"Error en la solicitud de PurchaseOrders: {str(e)}", 'status_code': 500}
    
    
#FUNCION GUARDADO OCC Y OCD1
def guardar_orden_compra_oc(detalles_seleccionados, solicitud, tipo, proveedor):
    try:
        # Buscar el proveedor en la base de datos
        proveedor_instance = OCRD.objects.get(CardCode=proveedor)
    except OCRD.DoesNotExist:
        return JsonResponse({'error': f'El proveedor con código {proveedor} no existe.'}, status=400)

    # Crear cabecera OCC
    serie_instance = Series.objects.get(CodigoSerie=solicitud.Serie)

    # Calcular el TotalOC sumando los totales de los detalles
    total_oc = sum(detalle.Precio * detalle.Quantity for detalle in detalles_seleccionados)

    # Determinar el TotalImpuestosOC
    if solicitud.TaxCode.Code == "IGV":  # Verificar si el TaxCode es IGV
        total_impuestos_oc = total_oc * 0.18  # Aplicar el 18%
    else:
        total_impuestos_oc = solicitud.TotalImp  # Mantener el valor original si no es IGV

    orden_compra_cabecera = OCC.objects.create(
        DocNumOC=OCC.objects.count() + 1,  # Generar un DocNum incremental
        SerieOC=serie_instance,
        SolicitanteOC=solicitud.ReqIdUser,
        DocTypeOC=tipo,
        DocDateOC=solicitud.DocDate,
        DocDueDateOC=solicitud.DocDueDate,
        SystemDateOC=date.today(),
        ProveedorOC=proveedor_instance,  # Asignar la instancia del proveedor
        MonedaOC=solicitud.moneda,
        TaxCodeOC=solicitud.TaxCode,
        TotalOC=total_oc,  # Total calculado
        TotalImpuestosOC=total_impuestos_oc + total_oc,  # Total de impuestos calculado
        CommentsOC=solicitud.Comments,
    )

    # Crear los detalles en OCD1
    detalles_ocd1 = []
    for detalle in detalles_seleccionados:
        detalle_ocd1 = OCD1.objects.create(
            NumDocOCD=orden_compra_cabecera,
            ItemCodeOCD=detalle.ItemCode,
            LineVendorOCD=proveedor_instance,  # Asignar la instancia del proveedor
            DescriptionOCD=detalle.Description,
            QuantityOCD=detalle.Quantity,
            UnidadMedidaOCD=detalle.UnidadMedida,
            AlmacenOCD=detalle.Almacen,
            CuentaMayorOCD=detalle.CuentaMayor,
            PrecioOCD=detalle.Precio,
            TotalOCD=detalle.Precio * detalle.Quantity,
            LineStatusOCD='C',
            DimensionOCD=detalle.idDimension,
            DocNumSAPOCD=None,  # Actualizar después
            BaseEntryOCD=detalle.NumDoc.DocNumSAP,  # Cambiado: usar DocNumSAP en lugar de DocEntry
            BaseLineOCD=detalle.LineCount_Indexado,  # Usar LineCount
            DocEntryOCD=detalle.NumDoc.DocEntry
        )
        detalles_ocd1.append(detalle_ocd1)

        # Marcar el detalle como cerrado
        detalle.LineStatus = 'C'
        detalle.save()

    # Actualizar `DocNumSAPOCD` después de enviar a SAP
    for detalle_ocd1 in detalles_ocd1:
        detalle_ocd1.DocNumSAPOCD = orden_compra_cabecera.DocNumSAPOC
        detalle_ocd1.save()

    # Actualizar el `TipoDoc` de todas las solicitudes relacionadas con los detalles seleccionados
    solicitudes_actualizadas = set(detalle.NumDoc for detalle in detalles_seleccionados)  # Conjunto de solicitudes únicas

    for solicitud in solicitudes_actualizadas:
        # Verificar si hay detalles pendientes con LineStatus 'A' o 'L'
        detalles_pendientes = PRQ1.objects.filter(NumDoc=solicitud.DocEntry, LineStatus__in=['A', 'L']).exists()

        if not detalles_pendientes:
            # Solo actualizar TipoDoc a 'OC' si NO hay detalles pendientes con 'A' o 'L'
            solicitud.TipoDoc = 'OC'
        else:
            # Si hay detalles pendientes, mantener TipoDoc como 'SOL'
            solicitud.TipoDoc = 'SOL'

        solicitud.save()

    return orden_compra_cabecera

# # LISTA DE ORDENES
class OrdenCompraListView(ValidatePermissionRequiredMixin2, ListView):
    model = OCC
    template_name = 'OrdenCompra/listar_orden_compra.html'
    required_groups = ['Jefe_Logistica', 'Jefe_de_Presupuestos']
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Listado de Ordenes de Compra'
        context['entity'] = 'Ordenes de Compra'
        return context

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return OCC.objects.prefetch_related(
            'detalles_oc',  # Asegúrate de que este es el related_name correcto
            Prefetch(
                'detalles_oc__NumDocOCD',  # Este sería un ejemplo de cómo traer detalles de OPRQ asociados a OCD1
                queryset=OPRQ.objects.prefetch_related(
                    'detalles_prq1'  # Aquí traes los detalles de PRQ1 asociados a OPRQ
                )
            )
        )

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
                
                position = 1  # Initialize position counter
                for orden in self.get_queryset():
                    item = orden.toJSON()
                    item['position'] = position  # Add position to item
                    detalles = []
                    for detalle in orden.detalles_oc.all():
                        detalle_dict = detalle.toJSON()  # Asegúrate de que detalle también tenga un método toJSON
                        detalles.append(detalle_dict)
                    item['detalles'] = detalles
                    item['origins'] = []
                    for detalle in orden.detalles_oc.all():
                        item['origins'].append({
                            'BaseEntryOCD': detalle.BaseEntryOCD,
                            'DescriptionOCD': detalle.DescriptionOCD,
                        })
                    data['data'].append(item)
                    position += 1  # Increment position counter
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
            'LineStatus'
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
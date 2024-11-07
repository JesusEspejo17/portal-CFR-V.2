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
                encabezado.DocStatus = "P" #P: pendiente, A: aprobado, R: rechazado C:cancelado
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
            msg = "Error al insertar datos maestros:" + {{str(e)}}
            render(request, template_name, {'error message': msg})
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
    model: OPRQ
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
                solicitudes = OPRQ.objects.filter(DocStatus='C').order_by('DocEntry')        
                for i in solicitudes:
                    data.append(i.toJSON())
            elif action == "showDetails":
                data = []
                for i in PRQ1.objects.filter(NumDoc=request.POST['id']):
                    data.append(i.toJSON())
            elif action=="getDetails":
                data = []
                for i in PRQ1.objects.filter(NumDoc=request.POST['code']):
                    data.append(i.toJSON())
            else:
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            data['error'] = {{str(e)}}
        return JsonResponse(data, safe=False)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Listado de Solicitudes'
        context['entity'] = 'OPRQ'
        return context
    
    def get_queryset(self):
        return OPRQ.objects.order_by('DocNum')

class ListSolicitudesCompra(ValidatePermissionRequiredMixin2, ListView):
    model: OPRQ
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
                    solicitudes = OPRQ.objects.filter(DocStatus='A').order_by('DocEntry')          
                for i in solicitudes:
                    data.append(i.toJSON())
            elif action == "showDetails":
                data = []
                for i in PRQ1.objects.filter(NumDoc=request.POST['id']):
                    data.append(i.toJSON())
            elif action=="getDetails":
                data = []
                for i in PRQ1.objects.filter(NumDoc=request.POST['code']):
                    data.append(i.toJSON())
            else:
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            data['error'] = {{str(e)}}
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
    
def solicitudContabilizar(request,id):
    Solicitud = OPRQ.objects.filter(pk=id)
    if request.method=="POST":
        try:
            if Solicitud:
                validate = Validaciones()
                Solicitud.update(DocStatus="C")
                data = json.loads(request.body)
                usuario = data.get('usuario', None)
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
    return JsonResponse({'error': 'Metodo no permitido'}, status=405)

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
                    validate = Validaciones()
                    Solicitud_object.update(DocStatus="C")
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
                    with transaction.atomic():
                        detalles = PRQ1.objects.filter(NumDoc=id)
                        if detalles.exists():
                            original_status = {detalle.pk: detalle.LineStatus for detalle in detalles}
                            checked_codes = {item.get('Code') for item in checked_prod}
                        else:
                            return JsonResponse({'error': 'Detalle no encontrado'}, status=404)
                        for detalle in detalles:
                            if detalle.Code in checked_codes:
                                if detalle.LineStatus != 'A':
                                    detalle.LineStatus = 'A'
                                    detalle.save()
                            else:
                                if detalle.LineStatus != 'R':
                                    detalle.LineStatus = 'R'
                                    detalle.save()
                    response = export_data_as_json(id)
                    response_content = json.loads(response.content)
                    error_message = response_content.get('error', 'Error desconocido')
                    if response.status_code != 200:
                        for detalle in detalles:
                            detalle.LineStatus = original_status.get(detalle.pk, detalle.LineStatus)
                            detalle.save()
                        return JsonResponse({'error': error_message}, status=response.status_code)
                    else:
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
            return JsonResponse({'success': "Éxito"}, status=200)
        except Exception as e:
            msg = f"Error al insertar datos maestros: {str(e)}"
            return JsonResponse({'error': msg}, status=500)
    
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
    
def solicitudAprobar(request,id):
    if request.method=="POST":
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
                for detalle in detalles:
                    if detalle.Code in checked_codes:
                        if detalle.LineStatus != 'A':
                            detalle.LineStatus = 'A'
                            detalle.save()
                    else:
                        if detalle.LineStatus != 'R':
                            detalle.LineStatus = 'R'
                            detalle.save()
                response = export_data_as_json(id)
                response_content = json.loads(response.content)
                error_message = response_content.get('error', 'Error desconocido')
                if response.status_code != 200:
                    for detalle in detalles:
                        detalle.LineStatus = original_status.get(detalle.pk, detalle.LineStatus)
                        detalle.save()
                    return JsonResponse({'error': error_message}, status=response.status_code)
                else:
                    validate = Validaciones()
                    Solicitud.update(DocStatus="A")
                    data = json.loads(request.body)
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
    return JsonResponse({'error': 'Metodo no permitido'}, status=405)

def solicitudRechazar(request,id):
    if request.method=="POST":
        try:
            data = json.loads(request.body)
            usuario = data.get('usuario', None)
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
                validate = Validaciones()
                Solicitud.update(DocStatus="R")
                data = json.loads(request.body)
                usuario = data.get('usuario', None)
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
    return JsonResponse({'error': 'Metodo no permitido'}, status=405)

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
            "RequriedDate": solicitud.DocDate,
            "DocumentLines": []
        }
        detalle = PRQ1.objects.filter(NumDoc=solicitud.DocEntry)
        for det in detalle:
            if det.LineStatus=='A':
                detalle_list = {
                    'ItemCode': det.ItemCode.ItemCode,
                    'LineVendor': det.LineVendor.CardCode,
                    "TaxCode": solicitud.TaxCode.Code,
                    'Quantity': det.Quantity,
                    'CostingCode': det.idDimension.descripcion if det.idDimension else 'null',
                    'Currency': det.Currency.MonedaAbrev if det.Currency else 'null'
                }
                oprq['DocumentLines'].append(detalle_list)
        data.append(oprq)
    json_data = json.dumps(data[0], indent=2, default=lambda o: o.isoformat() if isinstance(o, date) else None)
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



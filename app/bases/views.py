from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.views import generic
from django.http import HttpResponseRedirect, JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse_lazy

from erp.models import OPRQ, PRQ1

# Create your views here.

class MixinFormInvalid:
    def form_invalid(self,form):
        response = super().form_invalid(form)
        if self.request.is_ajax():
            return JsonResponse(form.errors, status=400)
        else:
            return response

class SinPrivilegios(LoginRequiredMixin, PermissionRequiredMixin, MixinFormInvalid):
    login_url = 'bases:login'
    raise_exception=False
    redirect_field_name="redirecto_to"

    def handle_no_permission(self):
        from django.contrib.auth.models import AnonymousUser
        if not self.request.user==AnonymousUser():
            self.login_url='bases:sin_privilegios'
        return HttpResponseRedirect(reverse_lazy(self.login_url))   

class Home(LoginRequiredMixin, generic.TemplateView):
    model: OPRQ
    template_name = 'bases/home.html'
    login_url='/admin'
    @method_decorator(csrf_exempt)
    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        user = self.request.user
        solicitudes_pendientes = OPRQ.objects.filter(DocStatus="P").count()
        
        solicitudes_pendientes_usuario = OPRQ.objects.filter(ReqIdUser=user.id).filter(DocStatus="P").count()
        solicitudes_totales = OPRQ.objects.filter(ReqIdUser=user.id).count()
        solicitudes_aprobadas =  OPRQ.objects.filter(ReqIdUser=user.id).filter(DocStatus="A").count()
        solicitudes_rechazadas =  OPRQ.objects.filter(ReqIdUser=user.id).filter(DocStatus="R").count()
        solicitudes_contabilizadas = OPRQ.objects.filter(ReqIdUser=user.id).filter(DocStatus="C").count()
        es_empleado = (user.groups.filter(name__in=['Empleado']).exists())
        if es_empleado:
            ultima_solicitud =  OPRQ.objects.filter(ReqIdUser=user.id).order_by('DocDate').order_by('DocEntry').last()
        else:
            ultima_solicitud =  OPRQ.objects.filter().order_by('DocDate').order_by('DocEntry').last()
        if ultima_solicitud:
            cant_ultima_solicitud = PRQ1.objects.filter(NumDoc=ultima_solicitud).count()
            if ultima_solicitud.DocStatus=='A':
                estado = "Aprobado"
                tipo = "success"
            elif ultima_solicitud.DocStatus=='R':
                estado = "Rechazado"
                tipo= "danger"
            elif ultima_solicitud.DocStatus=='P':
                estado = "Pendiente"
                tipo="warning"
            elif ultima_solicitud.DocStatus=='C':
                estado = "Contabilizado"
                tipo="success"
            else:
                estado="No especificado"
                tipo="secondary"
            if ultima_solicitud.DocType=='I':
                tipoDoc = "Artículo"
            elif ultima_solicitud.DocType=='S':
                tipoDoc = "Servicio"
        else:
            context = {'solicitudes_pendientes': solicitudes_pendientes, 
                'es_empleado': es_empleado,
                'solicitudes_pendientes_usuario': solicitudes_pendientes_usuario, 
                'title_usuario': 'Solicitudes realizadas pendientes: ', 
                'title': 'Solicitudes Pendientes de Aprobación: ',
                'title_ultima': 'Última Solicitud:',
                'title_contabilizados':'Solicitudes contabilizadas: ',
                'solicitudes_totales': solicitudes_totales,
                'solicitudes_aprobadas': solicitudes_aprobadas,
                'solicitudes_rechazadas': solicitudes_rechazadas,
                'solicitudes_contabilizadas': solicitudes_contabilizadas,
                'title_totales': 'Solicitudes Totales: ', 
                'title_aprobadas': 'Solicitudes Aprobadas: ',
                'title_rechazadas': 'Solicitudes Rechazadas: ',
                'tiene_solicitudes': False,
            }
            return self.render_to_response(context)

        context = {'solicitudes_pendientes': solicitudes_pendientes, 
            'es_empleado': es_empleado,
            'tipoDoc': tipoDoc,
            'solicitudes_pendientes_usuario': solicitudes_pendientes_usuario, 
            'title_usuario': 'Solicitudes realizadas pendientes: ', 
            'title': 'Solicitudes Pendientes de Aprobación: ',
            'title_ultima': 'Última Solicitud:',
            'title_contabilizados':'Solicitudes contabilizadas: ',
            'solicitudes_totales': solicitudes_totales,
            'solicitudes_aprobadas': solicitudes_aprobadas,
            'solicitudes_rechazadas': solicitudes_rechazadas,
            'ultima_solicitud': ultima_solicitud,
            'cant_ultima_solicitud': cant_ultima_solicitud,
            'solicitudes_contabilizadas': solicitudes_contabilizadas,
            'title_totales': 'Solicitudes Totales: ', 
            'title_aprobadas': 'Solicitudes Aprobadas: ',
            'title_rechazadas': 'Solicitudes Rechazadas: ', 
            'estado': estado,
            'tipo': tipo,
            'tiene_solicitudes':True
        }
        return self.render_to_response(context)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    
class HomeSinPrivilegios(LoginRequiredMixin, generic.TemplateView):
    login_url = "bases:login"
    template_name="bases/sin_privilegios.html"
    
    
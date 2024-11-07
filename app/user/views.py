from django.shortcuts import render
from django.views.generic import ListView, CreateView, DeleteView, TemplateView
from user.models import User
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from app.mixins import ValidatePermissionRequiredMixin
from django.http import JsonResponse, HttpResponseRedirect
from user.forms import UserForm
from django.contrib.messages.views import SuccessMessageMixin
from django.db import IntegrityError
# Create your views here.

class UserListView(ValidatePermissionRequiredMixin, ListView):
    model = User
    template_name = 'users/list.html'
    permission_required = 'user.view_user'
    @method_decorator(csrf_exempt)


    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == "searchdata":
                data = []
                position = 1
                for i in User.objects.all():
                    item = i.toJSON()
                    item['position'] = position
                    data.append(item)
                    position += 1
            else:
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Listado de Usuarios'
        context['entity'] = 'Usuarios'
        context['create_url'] =reverse_lazy('user:usercreate')
        context['list_url'] = reverse_lazy('user:userlist')
        return context


class UserCreateView(ValidatePermissionRequiredMixin, CreateView):
    model = User
    form_class = UserForm
    template_name = 'users/create.html'
    success_url = reverse_lazy('user:userlist')
    url_redirect = success_url
    permission_required = 'user.add_user'
    
    def form_valid(self, form):
        # Guarda la instancia del usuario
        self.object = form.save()

        # Redirige a success_url
        return HttpResponseRedirect(self.get_success_url())
    
    def form_invalid(self, form):
        # Renderiza la plantilla con los errores del formulario
        return self.render_to_response(self.get_context_data(form=form))
    
    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            try:
                # Usa form_valid para manejar el guardado y redirección
                return self.form_valid(form)
            except Exception as e:
                form.add_error(None, str(e))
        else:
            form.add_error(None, 'Formulario no válido.')

        # Renderiza la misma plantilla con errores si el formulario no es válido
        return self.render_to_response(self.get_context_data(form=form))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['create_url'] = reverse_lazy('user:userlist')
        context['list_url'] = self.success_url
        return context
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    
class UserDeleteView(DeleteView):
    model=User
    template_name = 'users/delete.html'
    context_object_name='obj'
    success_url = reverse_lazy('user:userlist')
    url_redirect = success_url
    success_message="Categoría Eliminada Satisfactoriamente"

class TestView(TemplateView):
    template_name="emails/new-email.html"


from django.shortcuts import redirect
from datetime import datetime

from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from django.contrib.auth.mixins import UserPassesTestMixin

class ValidatePermissionRequiredMixin2(UserPassesTestMixin):
    required_groups = []
    redirect_url = 'bases:sin_privilegios'
    def test_func(self):
        user = self.request.user
        if user.is_superuser or any(group.name in 'Administrador' for group in user.groups.all()):
            return True
        return any(group.name in self.required_groups for group in user.groups.all())
    
    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            return redirect(self.redirect_url)
        else:
            return super().handle_no_permission()

class ValidatePermissionRequiredMixin(object):
    permission_required = ''
    url_redirect = None

    def get_perms(self):
        if isinstance(self.permission_required, str):
            perms = (self.permission_required,)
        else:
            perms = self.permission_required
        return perms

    def get_url_redirect(self):
        if self.url_redirect is None:
            return reverse_lazy('bases:sin_privilegios')
        return self.url_redirect

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            user_groups = request.user.groups.values_list('name', flat=True)
            required_perms = self.get_perms()
            if any(request.user.has_perm(perm) for perm in required_perms):
                return super().dispatch(request, *args, **kwargs)
            elif any(group in user_groups for group in required_perms):
                return super().dispatch(request, *args, **kwargs)
        return HttpResponseRedirect(self.get_url_redirect())
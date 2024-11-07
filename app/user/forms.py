from django.forms import ModelForm, TextInput, Textarea, PasswordInput, SelectMultiple
from django.contrib.auth.models import Group
from user.models import User
from django import forms
from django.utils import timezone
from erp.models import *

class UserForm(ModelForm):
    departamento = forms.ModelChoiceField(
        queryset=Departamento.objects.all(),
        required=False,
        empty_label="Seleccione un departamento",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    class Meta:
        model = User
        fields = ['SAP_Code', 'username', 'password','last_login', 'first_name', 'last_name', 'email', 'image', 'UserType','groups','departamento', 'is_head_of_area']
        widgets = {
            'groups': forms.SelectMultiple(attrs={
                'id':'id-groups',
                'class': 'form-control select2',
                'style': 'width: 100%;',
                'required': 'required',
            })
        }
        exclude = ['user_permissions', 'last_login', 'date_joined', 'is_superuser','is_active','is_staff'],
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Añade el campo de Departamento en el formulario si el usuario es un Jefe de Área
        if self.instance and self.instance.pk:
            if self.instance.is_head_of_area:
                self.fields['departamento'].required = True
            else:
                self.fields['departamento'].required = False

    def save(self, commit=True):
        form = super()
        data = {}
        try:
            user = super().save(commit=False)
            pwd = self.cleaned_data.get('password', '')
            grupos = self.cleaned_data.get('groups', None)
            # Verifica si 'grupos' es un QuerySet o una lista
            if grupos:
            # Asegúrate de que 'grupos' sea una lista o un QuerySet
                if hasattr(grupos, 'all'):
                    grupos = grupos.all()
            # Verifica si algún grupo tiene el nombre 'Jefe_de_Area'
                if any(grupo.name == 'Jefe_De_Area' for grupo in grupos):
                    user.is_head_of_area = True
                    user.departamento = self.cleaned_data.get('departamento', None)
                else:
                    user.is_head_of_area = False
                    user.departamento = None
            else:
                user.is_head_of_area = False
                user.departamento = None
            if user.pk is None:
                user.set_password(pwd)
            else:
                us = User.objects.get(pk=user.pk)
                if pwd != us.password: 
                    user.set_password(pwd)
            if commit:
                user.last_login = timezone.now()
                user.save()
                self.save_m2m()
            return user
        except Exception as e:
            data['error'] = str(e)
        return data



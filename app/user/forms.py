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

# NUEVO FORM 
class UserEditForm(forms.ModelForm):
    departamento = forms.ModelChoiceField(
        queryset=Departamento.objects.all(),
        required=False,
        empty_label="Seleccione un departamento",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ['SAP_Code', 'username', 'password', 'first_name', 'last_name', 
                    'email', 'image', 'UserType', 'groups', 'departamento', 'is_head_of_area']
        widgets = {
            'groups': forms.SelectMultiple(attrs={
                'id': 'id-groups',
                'class': 'form-control select2',
                'style': 'width: 100%;',
            })
        }
        exclude = ['user_permissions', 'last_login', 'date_joined', 'is_superuser', 'is_active', 'is_staff']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Asegura que departamento tenga el valor guardado en base de datos
        if self.instance.departamento:
            self.fields['departamento'].initial = self.instance.departamento

    def clean(self):
        cleaned_data = super().clean()
        groups = cleaned_data.get('groups')
        departamento = cleaned_data.get('departamento')

        # Verifica si el grupo `Jefe_De_Area` está seleccionado
        is_jefe_de_area = any(group.name == 'Jefe_De_Area' for group in groups)
        
        if is_jefe_de_area and not departamento:
            self.add_error('departamento', 'Debe seleccionar un departamento para el rol de Jefe De Area')
        elif not is_jefe_de_area:
            # Si no es `Jefe_De_Area`, departamento no es necesario ni debe persistir
            cleaned_data['departamento'] = None

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        pwd = self.cleaned_data.get('password', '')

        # Actualiza el campo is_head_of_area en base a los grupos
        user.is_head_of_area = any(group.name == 'Jefe_De_Area' for group in self.cleaned_data.get('groups', []))
        
        # Borra departamento si no es Jefe de Área
        if not user.is_head_of_area:
            user.departamento = None  # Cambiado a None para borrar el valor del campo

        # Actualiza la contraseña solo si es nueva
        if user.pk is None or pwd != User.objects.get(pk=user.pk).password:
            user.set_password(pwd)

        if commit:
            user.save()
            self.save_m2m()

        return user

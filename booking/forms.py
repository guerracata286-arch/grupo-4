from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User, Group
from datetime import datetime, timedelta
from .models import Room, Material, Reservation, Blackout, RoomInventory

class ReservationForm(forms.Form):
    room = forms.ModelChoiceField(queryset=Room.objects.all(), label="Salón")
    date = forms.DateField(widget=forms.DateInput(attrs={"type":"date"}))
    start_time = forms.TimeField(widget=forms.TimeInput(attrs={"type":"time"}))
    end_time = forms.TimeField(widget=forms.TimeInput(attrs={"type":"time"}))

    def clean(self):
        cleaned = super().clean()
        s = cleaned.get("start_time"); e = cleaned.get("end_time")
        if s and e and s >= e:
            raise forms.ValidationError("La hora de inicio debe ser menor que la de término.")
        return cleaned

class BlackoutForm(forms.ModelForm):
    class Meta:
        model = Blackout
        fields = ["room", "start_datetime", "reason"]
        widgets = {
            "start_datetime": forms.DateTimeInput(attrs={"type":"datetime-local"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['start_datetime'].help_text = "El bloqueo será automáticamente de 45 minutos"

    def clean_start_datetime(self):
        start_datetime = self.cleaned_data.get('start_datetime')
        if start_datetime:
            # Calculate end datetime (45 minutes later)
            end_datetime = start_datetime + timedelta(minutes=45)
            
            # Store the calculated end datetime for later use
            self.calculated_end_datetime = end_datetime
        
        return start_datetime

    def clean(self):
        cleaned = super().clean()
        start_datetime = cleaned.get("start_datetime")
        
        if start_datetime:
            # Add the calculated end datetime to cleaned data
            cleaned['end_datetime'] = getattr(self, 'calculated_end_datetime', None)
        
        return cleaned

class MaterialForm(forms.ModelForm):
    class Meta:
        model = Material
        fields = ["name"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Nombre del material"})
        }

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text='Requerido. Ingresa una dirección de email válida.')
    first_name = forms.CharField(max_length=30, required=True, label='Nombre')
    last_name = forms.CharField(max_length=30, required=True, label='Apellidos')

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.is_active = True  # Activar automáticamente
        if commit:
            user.save()
            # Asignar automáticamente al grupo Docente
            docente_group, _ = Group.objects.get_or_create(name="Docente")
            user.groups.add(docente_group)
        return user

class InventoryForm(forms.ModelForm):
    class Meta:
        model = RoomInventory
        fields = ["room", "material", "quantity"]
        widgets = {
            "room": forms.Select(attrs={"class": "form-control"}),
            "material": forms.Select(attrs={"class": "form-control"}),
            "quantity": forms.NumberInput(attrs={"class": "form-control", "min": "0"})
        }

class InventoryUpdateForm(forms.Form):
    action = forms.ChoiceField(
        choices=[("add", "Agregar"), ("remove", "Quitar"), ("set", "Establecer")],
        widget=forms.Select(attrs={"class": "form-control"})
    )
    quantity = forms.IntegerField(
        min_value=0,
        widget=forms.NumberInput(attrs={"class": "form-control", "min": "0"})
    )


class AdminUserCreationForm(forms.ModelForm):
    """Formulario completo para crear usuarios desde el panel de administración"""
    password1 = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={"class": "form-control"})
    )
    password2 = forms.CharField(
        label="Confirmar contraseña",
        widget=forms.PasswordInput(attrs={"class": "form-control"})
    )
    groups = forms.ModelMultipleChoiceField(
        queryset=Group.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label="Grupos"
    )

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email", "is_staff"]
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control"}),
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "is_staff": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Las contraseñas no coinciden.")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.is_active = True
        if commit:
            user.save()
            # Guardar los grupos seleccionados
            groups = self.cleaned_data.get('groups')
            if groups:
                user.groups.set(groups)
        return user

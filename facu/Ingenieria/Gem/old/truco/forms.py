from django import forms
from django.contrib.auth.forms import UserCreationForm

class UserForm(UserCreationForm):
	telefono = forms.IntegerField()

class FormularioPrueba(forms.Form):
	nombre = forms.CharField(label="Decime tu nombre, por favor", max_length=100)
	telefono = forms.IntegerField()

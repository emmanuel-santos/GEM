from django import forms
from truco.constants import PUNTOS

class NuevaSalaForm(forms.Form):
    Nombre = forms.CharField(max_length=50)
    Puntos = forms.ChoiceField(widget=forms.RadioSelect,choices=[(15,'15'),(30,'30')])
    num_jug = forms.ChoiceField(label='Cantidad de jugadores',choices=[(2,'2'),(4,'4'),(6,'6')])


class MentirForm(forms.Form):
    Puntos = forms.ChoiceField(label='',choices=PUNTOS)
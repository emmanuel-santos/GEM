import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "trucoGemSite.settings")
django.setup()

from truco.models import *
from django.contrib.auth.models import User
from django.test import Client

for letra in "abcdef":
    a = User.objects.create_user(letra,"mail",letra)

Partida(nombre='dos',cantidad_jugadores=2).save()
for letra in "ab":
    c = Client()
    c.login(username=letra, password=letra)
    c.get('/sala/'+ str(Partida.objects.last().id))

Partida(nombre='cuatro',cantidad_jugadores=4).save()
for letra in "abcd":
    c = Client()
    c.login(username=letra, password=letra)
    c.get('/sala/'+ str(Partida.objects.last().id))

Partida(nombre='seis',cantidad_jugadores=6).save()
for letra in "abcdef":
    c = Client()
    c.login(username=letra, password=letra)
    c.get('/sala/'+ str(Partida.objects.last().id))



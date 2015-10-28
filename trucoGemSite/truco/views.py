from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth import logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.http import HttpResponseRedirect, HttpResponse
from truco.forms import *
from truco.models import Partida, Jugador, Carta
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import login
from django.db.models import F, Count


def vista_principal(request):
    if request.user.is_authenticated():
        return hall(request)
    else:
        return login(request,template_name='login.html')

@login_required
def salir_partida(request, ident):
    try:
        partida = Partida.objects.get(id = ident)
    except Partida.DoesNotExist:
        return HttpResponseRedirect('/')
    jugador = partida.jugador(request.user)
    equipo = jugador.equipo

    partida.equipos.exclude(id=equipo.id).update(puntos_partida=30)
    partida.terminada = True
    partida.save()

    return HttpResponseRedirect('/')

def new_user(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(form.cleaned_data['username'], 'default@default.com', form.cleaned_data['password1'])
            user.save()
            return HttpResponseRedirect("volver")
    else:
        form = UserCreationForm()
    return render(request, 'form.html', {'form':form})

def volver(request):
    if request.method == 'POST':
        return HttpResponseRedirect("/")
    else:
        return render(request, 'volver.html')

@login_required
def sala_input(request, ident, input):
    try:
        partida = Partida.objects.get(id = ident)
    except Partida.DoesNotExist:
        return HttpResponseRedirect('/')
    jugador = partida.jugador(request.user)

    partida.procesar_entrada(jugador,input)

    return HttpResponseRedirect('/sala/'+ str(ident))

@login_required
def partida_refresh(request, ident):
    return sala(request, ident, True)

@login_required
def sala(request, ident, refresh=False):
    try:
        partida = Partida.objects.get(id = ident)
    except Partida.DoesNotExist:
        return HttpResponseRedirect('/')
    jugador = partida.jugador(request.user)

    # Si hay slots vacios, el usuario los ocupa.
    if jugador == None:
        if not partida.esta_llena():
            partida.sumar_jugador(request.user)
            jugador = partida.jugador(request.user)

    # Elaborado de la respuesta
    resp = partida.mostrar_partida(jugador)

    # Form para mentir
    if request.method == 'POST':
        form = MentirForm(request.POST)
        if form.is_valid():
            jugador.puntos_cantados = form.cleaned_data['Puntos']
            jugador.save()
            partida.ultima_ronda.accion(jugador, 'mentir')
            return HttpResponseRedirect("/sala/" + str(ident))
    else:
        form = MentirForm()
    resp.update({'form':form})

    # Elegir template
    template = resp["template"] if refresh else "sala.html"

    return render(request, template, resp)

@login_required
def nueva_sala(request):
    if request.method == 'POST':
        form = NuevaSalaForm(request.POST)
        if form.is_valid():
            sala = Partida()
            sala.nombre=form.cleaned_data['Nombre']
            sala.puntos_max=form.cleaned_data['Puntos']
            sala.cantidad_jugadores=form.cleaned_data['num_jug']
            sala.save()
            return HttpResponseRedirect("sala/" + str(sala.id))
    else:
        form = NuevaSalaForm()
    return render(request, 'form.html', {'form':form})

@login_required
def hall(request):
    resp = {
        'hay_salas' : Partida.objects.all().count() != 0,
        'lista_salas' : Partida.objects.filter(terminada=False),
    }
    return render(request, 'hall.html', resp)

@login_required
def hall_select(request, categoria):
    categorias = {
        '0' : Partida.objects.filter(terminada=False),
        '1' : Partida.objects.annotate(Count('jugadores')).filter(jugadores__count__lt=2),
        '2' : Partida.objects.all(),
    }
    return render(request, 'hall_content.html', {'lista_salas':categorias[categoria]})

@login_required
def user(request,id):
    partidas = Partida.objects.annotate(Count('jugadores')).annotate(Count('rondas')).filter(jugadores__user__id=id).exclude(rondas__count=0)
    stats = {
        'totales' : partidas.count(),
        'ganadas' : Jugador.objects.filter(equipo__puntos_partida__gte=F('partida__puntos_max'),user__id=id).count(),
        'jugando' : partidas.filter(terminada=False).count(),
        'partidas' : partidas,
        'pageuser' : User.objects.get(id=id),
    }
    stats['perdidas'] = stats['totales'] - (stats['ganadas'] + stats['jugando'])
    return render(request, 'usuario.html', stats)

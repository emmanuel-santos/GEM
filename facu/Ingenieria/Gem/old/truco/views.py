from django.shortcuts import render_to_response
from django.template import RequestContext, loader
from django.shortcuts import get_object_or_404, render
from django.contrib.auth import login,logout,authenticate
from django.views.generic import TemplateView,FormView
from django.http import HttpResponseRedirect, HttpResponse
from .forms import UserForm, FormularioPrueba
from django.core.urlresolvers import reverse_lazy
from .models import Perfiles
from django import forms


class Registrarse(FormView):
	template_name = 'truco/index.html'
	form_class = UserForm
	success_url = reverse_lazy('sala')

	def form_valid(self, form):
		user = form.save()
		perfil = Perfiles()
		perfil.usuario = user
		perfil.telefono = 4780013
		perfil.save()
		returnsuper(Registrarse , self).form_valid(form)


def es_turno_de(user):
	return False

def es_mi_turno(func):
	def new_func(request):
		if not es_turno_de(request.user):
			return HttpResponse(request.user)
			return HttpResponseRedirect("/no_es_tu_turno")
		return func(request)

	return new_func

@es_mi_turno
def pruebita(request):
	if request.method == 'POST':
		formulario = FormularioPrueba(request.POST)
		if formulario.is_valid():
			if 'boton_ok' in request.POST:
				return HttpResponse("ok")
			else:
				return HttpResponse("Cancel")
			modelo = Perfiles(usuario=formulario.cleaned_data['nombre'], telefono=formulario.cleaned_data['telefono'])
			modelo.save()
			return HttpResponse("Hola, " + formulario.cleaned_data['nombre'] + " fuiste agregado a nuestra base de datos")
	else:
		formulario = FormularioPrueba()
	return render(request, 'truco/pruebita_template.html', {'formulario':formulario})


def Login(request):
    if Perfiles.objects.filter(usuario=request.user):
        return HttpResponseRedirect("/sala")
 
    ctx = {}
    if request.method == "GET":
        form = nickname(request.POST)
        ctx['form'] = form
        if form.is_valid():
            nombre = form.cleaned_data['nombre']
            if Perfiles.objects.filter(username= nombre):
                ctx['nombre'] =  nombre
                return render_to_response("error/UsuarioExiste.html",ctx,context_instance=RequestContext(request))
            else:
                Perfiles.objects.create_user(username=nombre,password=CLAVE)
                usuario = authenticate(username=nombre,password=CLAVE)
                login(request,usuario)
                # Si vino a registr por login required lo dirijo a esa url, C.C. a la sala
                url = request.GET.get('next', "sala")
                return HttpResponseRedirect(url)
        else:
            return render_to_response("error/SinNickname.html",ctx,context_instance=RequestContext(request))
    else:
        return render_to_response("registro.html",ctx,context_instance=RequestContext(request))

def nada(request):
	nada = "Bienvenido al juego <br> *agita las manitos*"
	return HttpResponse(nada)

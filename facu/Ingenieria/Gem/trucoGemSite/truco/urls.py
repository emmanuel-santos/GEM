from django.conf.urls import patterns, include, url
from truco import views

urlpatterns = patterns('',
    url(r'^$', views.vista_principal, name='home'),
    url(r'^hall/(?P<categoria>[0-9]+)', views.hall_select, name='hall_select'),
    url(r'^new_user$', views.new_user, name='register'),
    url(r'^nueva_sala$', views.nueva_sala, name='nueva_sala'),
    url(r'^sala/(?P<ident>\w+)/abandonar', views.salir_partida, name='salir'),
    url(r'^sala/(?P<ident>\w+)/refresh$', views.partida_refresh , name='partida_refresh'),
    url(r'^sala/(?P<ident>\w+)/(?P<input>[\w-]+)', views.sala_input, name='input'),
    url(r'^sala/(?P<ident>\w+)', views.sala, name='sala'),
    url(r'^user/(?P<id>[0-9]+)', views.user, name='perfil_de_usuario'),
    url(r'^volver', views.volver, name='volver'),
    url(r'^cerrar', 'django.contrib.auth.views.logout_then_login', name='cerrar'),
)

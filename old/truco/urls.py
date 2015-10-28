from django.conf.urls import patterns, include, url
from .views import Registrarse
from truco import views

urlpatterns = patterns('',
	url(r'^$' , views.Login, name='login'),
	url(r'^sala/$' , views.nada, name='sala'),
	url(r'^pruebita/$', views.pruebita, name='lalal')
)

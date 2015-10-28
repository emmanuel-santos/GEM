from django.db import models
from django.contrib.auth.models import User

class Perfiles(models.Model):
	usuario = models.CharField(max_length=200)
	telefono = models.IntegerField()

	def __unicode__(self):
		return self.usuario

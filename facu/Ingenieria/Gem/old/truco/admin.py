from django.contrib import admin
from truco.models import Perfiles

class LoginAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Nombre', {'fields': ['name']})
    ]

admin.site.register(Perfiles)

from django.contrib import admin
#permettre a un admin d'enregistrer les noms

from .models import *

admin.site.register(Employe)


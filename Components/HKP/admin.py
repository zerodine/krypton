from django.contrib import admin
from Components.HKP import models

admin.site.register(models.Identity)
admin.site.register(models.Publickey)

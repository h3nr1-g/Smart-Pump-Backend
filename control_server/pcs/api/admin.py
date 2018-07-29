from django.contrib import admin
from api import models

admin.site.register(models.Pump)
admin.site.register(models.TransmittedTiming)
admin.site.register(models.ServiceTask)
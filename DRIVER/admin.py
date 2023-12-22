# Register your models here.
from django.contrib import admin

from .models import Camion, Driver, Market, Trip

admin.site.register(Camion)
admin.site.register(Driver)
admin.site.register(Market)
admin.site.register(Trip)
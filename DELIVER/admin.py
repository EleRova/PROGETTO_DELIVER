# Register your models here.
from django.contrib import admin

from .models import Driver, Market, Trip, Temperature

admin.site.register(Driver)
admin.site.register(Market)
admin.site.register(Trip)
admin.site.register(Temperature)
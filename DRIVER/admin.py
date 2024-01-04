# Register your models here.
from django.contrib import admin

from .models import Driver, Market, Trip

admin.site.register(Driver)
admin.site.register(Market)
admin.site.register(Trip)
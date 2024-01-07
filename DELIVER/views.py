# Create your views here.
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404
from .login import LoginForm
from .models import Driver, Market, Temperature, Trip
from datetime import datetime
from django.core import serializers
import subprocess
import random
import threading
import time




def index(request):
    return HttpResponse("Hello, world. You're at the PCC index.")


def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            queryset = Driver.objects.filter(username=username, password=password)

            if queryset.exists():
                # Do something if the values exist in the database
                request.session['driver']= serializers.serialize('json', [queryset.first()])
                return render(request, 'home.html', {'driver': queryset.first()})
            else:
                # Do something if the values don't exist in the database
                return render(request, 'login.html', {'form': form, 'error': 'Invalid login credentials'})

    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

def driver_markets(request):
    return render(request, 'lista_negozi.html', {'market': Market.objects.all().values(), 'market_id': 0})

def send_telegram_message(request):
    temperature_value=float(request.GET.get('temperature', None))
    if temperature_value is not None:
        temperature = Temperature.objects.create(temperatura_registrata=temperature_value)
        temperature.save()
        if temperature_value>-7:
            subprocess.run(['telegram-send', "La temperatura è fuori range!"], check = True)
    market_id = request.Get.get('market_id', None)
    return render(request, 'lista_negozi.html', {'market': Market.objects.all().values(), 'market_id': market_id})


def driver_end_deliveries(request):
    return render(request, 'fine_giro.html')





def inizio_consegna(request, market_id):
    driver = list(serializers.deserialize("json", request.session.get('driver', None)))
    if driver:
        driver_data=driver[0].object
        market = get_object_or_404(Market,id_negozio = market_id)
        trip = Trip.objects.create(autista=driver_data, negozio=market, data_ora_partenza=datetime.now())
        request.session['market_id'] = market_id
        print(market_id)
        print(trip.id)
        return render(request, 'lista_negozi.html', {'market': Market.objects.all().values(), 'trip_id':trip.id, 'market_id':market_id-1})
    else:
        return JsonResponse({'error':'driver not found in session'})

def consegna_effettuata(request, trip_id):
    trip=get_object_or_404(Trip, id =trip_id)
    trip.data_ora_arrivo=datetime.now()
    print(trip.data_ora_arrivo)
    market_id= request.session.get('market_id', None)
    print(market_id)
    market = get_object_or_404(Market, id_negozio=market_id)
    ora_arrivo=datetime.strptime(trip.data_ora_arrivo.strftime("%H:%M:%S"),"%H:%M:%S")
    fine_ora = datetime.strptime(market.fine_fascia_consegna.strftime("%H:%M:%S"),"%H:%M:%S")
    ritardo=False
    if ora_arrivo > fine_ora:
        ritardo = True
        tempo_ritardo = ora_arrivo - fine_ora
        trip.tempo_ritardo=str(tempo_ritardo)
    trip.ritardo =ritardo
    trip.save()
    del request.session['market_id']
    if market_id == Market.objects.all().__len__():
        return driver_end_deliveries(request)
    else:
        return render(request, 'lista_negozi.html', {'market': Market.objects.all().values(), 'market_id': market_id})


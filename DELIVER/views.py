# Create your views here.
import os

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404
from .login import LoginForm
from .models import Driver, Market, Temperature, Trip
from datetime import datetime
from django.core import serializers
import subprocess
from google.cloud import bigquery

credential_path = "DELIVER/templates/credentials.json"
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credential_path


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
    driver = list(serializers.deserialize("json", request.session.get('driver', None)))
    driver_data=driver[0].object
    print(driver_data)
    return render(request, 'lista_negozi.html', {'market': Market.objects.all().values(), 'market_id': -1, 'driver': driver_data})

def send_telegram_message(request):
    temperature_value=float(request.GET.get('temperature', None))
    if temperature_value is not None:
        data_ora=datetime.now()
        print(temperature_value)
        temperature = Temperature.objects.create(temperatura_registrata=temperature_value, data_ora_rilevamento=data_ora)
        temperature.save()
        insert_bigquery_temp('pcloud-407811', 'deliver_dataset', 'temperature', temperature_value, data_ora)
        if temperature_value>-7:
            subprocess.run(['telegram-send', "La temperatura è fuori range!"], check = True)
    market_id = request.GET.get('market_id', None)
    return render(request, 'lista_negozi.html', {'market': Market.objects.all().values(), 'market_id': market_id})

def insert_bigquery_temp(project_id,dataset_id,table_id, temperature_value, data_ora):
    client = bigquery.Client()
    table_full_id = f'{project_id}.{dataset_id}.{table_id}'
    errors = client.insert_rows_json(table_full_id, [{'temperatura_registrata':temperature_value, 'data_ora_rilevamento':data_ora.strftime('%Y-%m-%d %H:%M:%S')}])  # Make an API request.
    if errors == []:
        print("New rows have been added.")
    else:
        print("Encountered errors while inserting rows: {}".format(errors))
    return

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
    else:
        tempo_ritardo = '00:00:00'
    trip.ritardo =ritardo
    trip.save()
    insert_bigquery_rit('pcloud-407811', 'deliver_dataset', 'Ritardi', trip.data_ora_partenza, trip.data_ora_arrivo, ritardo, trip.autista.id_autista, trip.negozio.id_negozio, tempo_ritardo)
    del request.session['market_id']
    if market_id == Market.objects.all().__len__():
        return driver_end_deliveries(request)
    else:
        return render(request, 'lista_negozi.html', {'market': Market.objects.all().values(), 'market_id': -1})

def insert_bigquery_rit(project_id,dataset_id,table_id, data_ora_partenza, data_ora_arrivo, ritardo, autista, negozio, tempo_ritardo ):
    client = bigquery.Client()
    table_full_id = f'{project_id}.{dataset_id}.{table_id}'
    if ritardo == True:
        ritardo = 1
    else:
        ritardo = 0
    errors = client.insert_rows_json(table_full_id, [{'data_ora_partenza':data_ora_partenza.strftime('%Y-%m-%d %H:%M:%S'), 'data_ora_arrivo':data_ora_arrivo.strftime('%Y-%m-%d %H:%M:%S'), 'ritardo':ritardo, 'autista_id':autista, 'negozio_id':negozio, 'tempo_ritardo':str(tempo_ritardo)}])  # Make an API request.
    if errors == []:
        print("New rows have been added.")
    else:
        print("Encountered errors while inserting rows: {}".format(errors))
    return

def urto(request):
    subprocess.run(['telegram-send', "L'autista ha avuto un incidente!"], check=True)
    market_id = request.GET.get('market_id', None)
    return render(request, 'lista_negozi.html', {'market': Market.objects.all().values(), 'market_id': market_id})
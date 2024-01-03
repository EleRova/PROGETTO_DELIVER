# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .login import LoginForm
from .models import Driver, Market, Temperature
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
                return render(request, 'home.html', {'driver': queryset.first()})
            else:
                # Do something if the values don't exist in the database
                return render(request, 'login.html', {'form': form, 'error': 'Invalid login credentials'})

    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

def driver_markets(request):
    t.start()

    return render(request, 'lista_negozi.html', {'market': Market.objects.all().values()})

def generate_temperature():
    while True:
        valore_temp = random.uniform(-20, 5)
        if valore_temp > -7:
            subprocess.run(['telegram-send', "La temperatura è fuori range!"], check=True)
        temperature = Temperature.objects.create(temperatura_registrata=valore_temp)
        temperature.save()
        global stop
        if stop:
            break
        time.sleep(5)


def driver_enddeliveries(request):
    global stop
    stop = True
    t.join()
    return render(request, 'fine_giro.html')

stop = False
t = threading.Thread(target=generate_temperature)
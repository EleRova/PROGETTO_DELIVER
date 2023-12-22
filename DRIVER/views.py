# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .login import LoginForm
from .models import Driver


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
                return render(request, 'home.html', {'driver': queryset})
            else:
                # Do something if the values don't exist in the database
                return render(request, 'login.html', {'form': form, 'error': 'Invalid login credentials'})

    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

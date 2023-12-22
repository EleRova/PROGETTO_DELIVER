f# Create your models here.
from django.db import models


class Camion(models.Model):
    targa = models.CharField(max_length=7, unique=True)
    portata = models.PositiveIntegerField()
    immatricolazione = models.DateField()


class Market(models.Model):
    id_negozio = models.PositiveIntegerField(unique=True)
    nome_negozio = models.CharField(max_length=50)
    proprietario = models.CharField(max_length=50)
    indirizzo = models.CharField(max_length=100)
    latitudine = models.DecimalField(max_digits=17, decimal_places=15)
    longitudine = models.DecimalField(max_digits=17, decimal_places=15)


class Driver(models.Model):
    id_autista = models.PositiveIntegerField(unique=True)
    nome = models.CharField(max_length=50)
    cognome = models.CharField(max_length=50)
    email = models.CharField(max_length=50)
    cellulare = models.CharField(max_length=10)
    username = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=50)

    def __str__(self):# to string di java
        return str(self.id_autista) + ' ' + self.nome + ' ' + self.cognome


class Trip(models.Model):
    autista = models.ForeignKey(Driver, on_delete=models.CASCADE)
    targa = models.ForeignKey(Camion, on_delete=models.CASCADE)
    negozio = models.ForeignKey(Market, on_delete=models.CASCADE)
    data_partenza = models.DateTimeField()
    ritardo =models.BooleanField(default=False)
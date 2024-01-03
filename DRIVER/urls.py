from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path('login/', views.user_login, name='loginDriver'),
    path('negozi/', views.driver_markets, name="negozi"),
    path('fine/', views.driver_enddeliveries, name="fine"),
]
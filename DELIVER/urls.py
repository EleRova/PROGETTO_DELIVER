from django.urls import path

from . import views

urlpatterns = [
    path('login/', views.user_login, name='loginDriver'),
    path('negozi/', views.driver_markets, name="negozi"),
    path('fine/', views.driver_end_deliveries, name="fine"),
    path('send_telegram_message/', views.send_telegram_message, name="send_telegram_message"),
    path('negozi/<int:market_id>', views.inizio_consegna, name="inizio_consegna"),
    path('consegna/<int:trip_id>', views.consegna_effettuata, name="consegna_effettuata"),
    path('urto/', views.urto, name="urto"),
]
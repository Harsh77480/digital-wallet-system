# wallets/urls.py
from django.urls import path
from .views import HealthView, ReserveFundsView

urlpatterns = [
    path("reserve", ReserveFundsView.as_view()),
    path("health", HealthView.as_view()),

]
    
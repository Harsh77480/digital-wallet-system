# transactions/urls.py
from django.urls import path
from .views import TransferView

urlpatterns = [
    path("transfer", TransferView.as_view()),
]

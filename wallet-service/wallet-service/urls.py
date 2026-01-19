# wallet_service/urls.py
from django.urls import include, path
from django.contrib import admin

urlpatterns = [
    path("", include("wallets.urls")),
    path('admin/', admin.site.urls),

]

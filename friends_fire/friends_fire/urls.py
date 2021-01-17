
from django.contrib import admin
from django.urls import path, include
import notify.urls

urlpatterns = [
    path('', include('playground.urls')),
    path('notifications/', include('notify.urls'),),
]

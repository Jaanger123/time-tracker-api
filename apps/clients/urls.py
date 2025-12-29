from django.urls import path

from .views import *


urlpatterns = [
    path('', ClientListView.as_view(), name='clients-list')
]

from django.urls import path
from . import views

urlpatterns = [
    path("time", views.time),
    path("sum", views.sum),
]

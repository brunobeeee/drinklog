from django.urls import path

from . import views

urlpatterns = [
    path("penis", views.index, name="index"),
]
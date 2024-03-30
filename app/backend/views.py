from django.shortcuts import render
from django.views.generic import ListView
from drinklog.models import Log

# Create your views here.
class LogList(ListView):
    model = Log

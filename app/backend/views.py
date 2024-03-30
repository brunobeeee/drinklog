from django.shortcuts import render
from django.views.generic import ListView
from drinklog.models import Log

# Create your views here.
class LogList(ListView):
    model = Log
    #template_name = './templates/log_list.html'
    context_object_name = 'logs'
    ordering = ['-date']

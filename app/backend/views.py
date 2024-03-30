from django.shortcuts import render
from django.views.generic import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy

from drinklog.models import Log

class LogList(ListView):
    model = Log
    context_object_name = 'logs'

class LogCreate(CreateView):
    model = Log
    fields = '__all__'
    success_url = reverse_lazy('list-logs')

class LogUpdate(UpdateView):
    model = Log
    fields = '__all__'
    success_url = reverse_lazy('list-logs')

class LogDelete(DeleteView):
    model = Log
    context_object_name = 'logs'
    success_url = reverse_lazy('list-logs')

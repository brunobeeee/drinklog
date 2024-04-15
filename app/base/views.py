from datetime import datetime, timedelta

import pandas as pd
import plotly.express as px
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.db import transaction
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
# Imports for Reordering Feature
from django.views import View
from django.views.generic.detail import DetailView
from django.views.generic.edit import (CreateView, DeleteView, FormView,
                                       UpdateView)
from django.views.generic.list import ListView

from .forms import PositionForm
from .models import Log


class CustomLoginView(LoginView):
    template_name = "base/login.html"
    fields = "__all__"
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy("logs")


class RegisterPage(FormView):
    template_name = "base/register.html"
    form_class = UserCreationForm
    redirect_authenticated_user = True
    success_url = reverse_lazy("logs")

    def form_valid(self, form):
        user = form.save()
        if user is not None:
            login(self.request, user)
        return super(RegisterPage, self).form_valid(form)

    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect("logs")
        return super(RegisterPage, self).get(*args, **kwargs)


class LogList(LoginRequiredMixin, ListView):
    model = Log
    context_object_name = "logs"

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(user=self.request.user)

        search_input = self.request.GET.get("search-area") or ""
        if search_input:
            queryset = queryset.filter(date__contains=search_input)

        return queryset.order_by("-date")  # Sortiere nach Datum absteigend


class LogDetail(LoginRequiredMixin, DetailView):
    model = Log
    context_object_name = "log"
    template_name = "base/log.html"


class LogCreate(LoginRequiredMixin, CreateView):
    model = Log
    fields = ["date", "intensity", "overdrive"]
    success_url = reverse_lazy("logs")

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(LogCreate, self).form_valid(form)

    def get_initial(self):
        initial = super().get_initial()
        initial["date"] = datetime.now() - timedelta(days=1)
        return initial


class LogUpdate(LoginRequiredMixin, UpdateView):
    model = Log
    fields = ["date", "intensity", "overdrive"]
    success_url = reverse_lazy("logs")


class DeleteView(LoginRequiredMixin, DeleteView):
    model = Log
    context_object_name = "log"
    success_url = reverse_lazy("logs")

    def get_queryset(self):
        owner = self.request.user
        return self.model.objects.filter(user=owner)


class LogReorder(View):
    def post(self, request):
        form = PositionForm(request.POST)

        if form.is_valid():
            positionList = form.cleaned_data["position"].split(",")

            with transaction.atomic():
                self.request.user.set_log_order(positionList)

        return redirect(reverse_lazy("logs"))


def logplot(request):
    all_logs = Log.objects.all()
    dates = [log.date for log in all_logs]
    intensities = [log.intensity for log in all_logs]

    df = pd.DataFrame({"date": dates, "intensity": intensities})
    fig_bar = px.bar(
        df,
        x="date",
        y="intensity",
        title="Drinklog Plot",
        labels={"intensity": "Intensity", "date": "Date"},
        color="intensity",
        color_continuous_scale=["green", "yellow", "red"]
    )
    fig_bar.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color='white',
        title_font_family='Jost',
        modebar_orientation='v',)
    bar_chart = fig_bar.to_html(full_html=False, include_plotlyjs=False)

    return render(request, "base/log_plot.html", {"bar_chart": bar_chart})

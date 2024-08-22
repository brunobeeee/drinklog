import calendar
import json
from datetime import date, datetime, timedelta
import random

import pandas as pd
import plotly.express as px
from django import forms
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic.detail import DetailView
from django.views.generic.edit import (CreateView, DeleteView, FormView,
                                       UpdateView)
from django.views.generic.list import ListView

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

        return queryset.order_by("-date")  # Sort descending by date

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_query"] = self.request.GET.get(
            "search-area", ""
        )

        # Choose a random icon for the overdrive col
        icons = [
            'fa-person-falling-burst',
            'fa-skull',
            'fa-skull-crossbones',
            'fa-bolt'
        ]

        context['random_icon'] = random.choice(icons)

        return context


class LogCreate(LoginRequiredMixin, CreateView):
    model = Log
    fields = ["date", "intensity", "overdrive"]
    success_url = reverse_lazy("logs")

    def form_valid(self, form):
        date = form.cleaned_data["date"]

        # Check if a log with this date exists
        existing_log = Log.objects.filter(date=date, user=self.request.user).first()

        if existing_log:  # Combine them
            existing_log.intensity = min(
                existing_log.intensity + form.cleaned_data["intensity"], 25
            )
            existing_log.overdrive = (
                existing_log.overdrive or form.cleaned_data["overdrive"]
            )
            existing_log.save()
            return redirect(self.success_url)
        else:  # Create a new one
            form.instance.user = self.request.user
            return super(LogCreate, self).form_valid(form)

    def get_initial(self):
        initial = super().get_initial()
        initial["date"] = datetime.now() - timedelta(days=1)
        return initial

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields["date"].widget = forms.DateInput(attrs={"type": "date"})
        form.fields["intensity"].widget = forms.TextInput(
            attrs={"type": "range", "min": "0", "max": "25", "value": "0"}
        )
        return form


class LogUpdate(LoginRequiredMixin, UpdateView):
    model = Log
    fields = ["date", "intensity", "overdrive"]
    success_url = reverse_lazy("logs")

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields["date"].disabled = True
        form.fields["date"].widget.attrs["readonly"] = True
        form.fields["date"].widget = forms.DateInput(
            attrs={"type": "date", "readonly": "readonly"}
        )
        form.fields["intensity"].widget = forms.TextInput(
            attrs={"type": "range", "min": "0", "max": "25", "value": "0"}
        )
        return form


class DeleteView(LoginRequiredMixin, DeleteView):
    model = Log
    context_object_name = "log"
    success_url = reverse_lazy("logs")

    def get_queryset(self):
        owner = self.request.user
        return self.model.objects.filter(user=owner)


from datetime import datetime, timedelta


def logplot(request):
    current_user = request.user

    all_logs = Log.objects.all()
    users = [log.user for log in all_logs]
    dates = [log.date for log in all_logs]
    intensities = [log.intensity for log in all_logs]
    overdrives = [log.overdrive for log in all_logs]

    # Create df
    df = pd.DataFrame(
        {
            "user": users,
            "date": dates,
            "intensity": intensities,
            "overdrive": overdrives,
        }
    )
    # Filter for current user
    df = df[df["user"] == current_user]

    # Add color column with black color when overdrive==True
    df["color"] = df["overdrive"].apply(lambda x: "black" if x else "yellow")

    # Creation of the plot
    fig = px.bar(
        df,
        x="date",
        y="intensity",
        title="",
        labels={"intensity": "Intensity", "date": "Date"},
        color="color",
        color_discrete_map={"black": "#090B0B", "yellow": "#D78F09"},
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#090B0B",
        title_font_family="Jost",
        coloraxis_showscale=False,
        xaxis_title=None,
        yaxis_title=None,
        showlegend=False,
        margin=dict(l=0, r=30, t=20, b=100),
    )

    fig.update_yaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor="#D2DADA",
        zeroline=True,
        zerolinecolor="#D2DADA",
    )

    fig.update_traces(
        hoverlabel=dict(
            font_size=16,
            font_family="Montserrat, Jost, sans-serif",
        )
    )

    fig.update_traces(hovertemplate="<b>Intensity: %{y}</b><br>%{x}<extra></extra>")

    bar_chart = fig.to_html(
        full_html=False, include_plotlyjs=False, config={"displayModeBar": False}
    )

    return render(
        request,
        "base/log_plot.html",
        {"bar_chart": bar_chart},
    )

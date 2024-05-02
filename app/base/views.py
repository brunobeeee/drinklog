from datetime import datetime, timedelta, date

import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
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
        )  # Suchtext an das Template übergeben
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
    df_current_user = df[df["user"] == current_user]

    # Add color column with black values when overdrive==True
    df_current_user["color"] = df_current_user.apply(
        lambda row: 0 if row["overdrive"] else row["intensity"], axis=1
    )

    # Creation of the plot for all data
    fig_bar_all = px.bar(
        df_current_user,
        x="date",
        y="intensity",
        labels={"intensity": "Intensity", "date": "Date"},
        color=df_current_user["color"],
        color_continuous_scale=[
            "black",
            "#00B86B",
            "#36AE53",
            "#6CA43A",
            "#A29A22",
            "#D78F09",
            "#D57016",
            "#D25122",
            "#D0322F",
            "#CD133B",
        ],
    )
    fig_bar_all.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="white",
        title_font_family="Jost",
        modebar_orientation="v",
        coloraxis_showscale=False,
    )
    bar_chart_all = fig_bar_all.to_html(full_html=False, include_plotlyjs=False)

    # Erstellen eines Datumsbereichs für eine ganze Woche
    start_date = date.today() - timedelta(days=date.today().weekday())  # Montag dieser Woche
    end_date = start_date + timedelta(days=6)  # Sonntag dieser Woche

    # Filter data for the current week
    current_week_logs = df_current_user[(df_current_user["date"] >= start_date) & (df_current_user["date"] <= end_date)]

    # Creation of the plot for the current week
    fig_bar_current_week = px.bar(
        current_week_logs,
        x="date",
        y="intensity",
        labels={"intensity": "Intensity", "date": "Date"},
        color=current_week_logs["color"],
        color_continuous_scale=[
            "black",
            "#00B86B",
            "#36AE53",
            "#6CA43A",
            "#A29A22",
            "#D78F09",
            "#D57016",
            "#D25122",
            "#D0322F",
            "#CD133B",
        ],
    )

    # Manuelle Festlegung des Bereichs der x-Achse auf eine ganze Woche
    fig_bar_current_week.update_xaxes(range=[start_date, end_date])

    fig_bar_current_week.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="white",
        title_font_family="Jost",
        modebar_orientation="v",
        coloraxis_showscale=False,
    )
    bar_chart_last_week = fig_bar_current_week.to_html(full_html=False, include_plotlyjs=False)

    return render(
        request,
        "base/log_plot.html",
        {"bar_chart_all": bar_chart_all, "bar_chart_last_week": bar_chart_last_week},
    )

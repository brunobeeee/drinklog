import calendar
import json
import random
from datetime import date, datetime, timedelta

import numpy as np
import pandas as pd
import plotly
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
from django.utils import timezone
from django.db.models import Sum

from .models import Log


class CustomLoginView(LoginView):
    template_name = "base/login.html"
    fields = "__all__"
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy("logs")



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
        context["search_query"] = self.request.GET.get("search-area", "")
        context["username"] = self.request.user.username

        # Choose a random icon for the overdrive col
        icons = [
            "fa-person-falling-burst",
            "fa-skull",
            "fa-skull-crossbones",
            "fa-bolt",
        ]

        context["random_icon"] = random.choice(icons)

        # Calculate #days since last log
        latest_log = self.get_queryset().first()
        if latest_log:
            days_since_last_log = (timezone.now().date() - latest_log.date).days
            context["days_since_last_log"] = days_since_last_log
        else:
            context["days_since_last_log"] = None

        # Sum all intensities of last week/month
        today = timezone.now().date()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)

        week_intensity_sum = self.get_queryset().filter(date__gte=week_ago).aggregate(Sum('intensity'))['intensity__sum'] or 0
        month_intensity_sum = self.get_queryset().filter(date__gte=month_ago).aggregate(Sum('intensity'))['intensity__sum'] or 0

        context["week_intensity_sum"] = week_intensity_sum
        context["month_intensity_sum"] = month_intensity_sum

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

    # Normal plot
    fig = px.bar(
        df,
        x="date",
        y="intensity",
        title="",
        labels={"intensity": "Intensity", "date": "Date"},
        color="color",
        color_discrete_map={"black": "#272727", "yellow": "#C8C2FF"},
    )
    pre_format_fig(fig)
    fig.update_traces(hovertemplate="<b>Intensity: %{y}</b><br>%{x}<extra></extra>")

    fig.update_xaxes(
        tickformat="%b %d",  # '%b' for short month names
    )

    # Year-section plot
    df["date"] = pd.to_datetime(df["date"])

    min_date = df["date"].min()
    max_date = df["date"].max()

    # Create a df with all dates in the years touched by the df
    date_range = pd.date_range(
        start=min_date.replace(month=1, day=1),
        end=max_date.replace(month=12, day=31),
        freq="D",
    )
    full_df = pd.DataFrame(date_range, columns=["date"])

    # Merge dates
    full_df = pd.merge(full_df, df, on="date", how="left")

    # Fill 'intensity' with 0
    full_df.fillna({"intensity": 0}, inplace=True)

    # Create plot
    fig2 = px.histogram(
        full_df,
        x="date",
        y="intensity",
        histfunc="avg",
        title="",
        nbins=12,
    )
    pre_format_fig(fig2)
    fig2.update_layout(bargap=0.1)

    fig2.update_traces(
        xbins_size="M1",
        marker_color="#C8C2FF",
        hovertemplate="<b>Avg Intensity: %{y}</b><extra></extra>",
    )

    fig2.update_xaxes(
        tickformat="%b",  # '%b' for short month names
        dtick="M1",  # show a tick for every month
        tick0="2000-01-15",  # places the ticklabels in the middle of the month
    )

    # Serialize plots
    plot = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    plot_year = json.dumps(fig2, cls=plotly.utils.PlotlyJSONEncoder)

    context = {
        "plot": plot,
        "plot_year": plot_year,
    }

    return render(request, "base/log_plot.html", context)


def pre_format_fig(fig):
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#090B0B",
        title_font_family="Jost",
        coloraxis_showscale=False,
        xaxis_title=None,
        yaxis_title=None,
        showlegend=False,
        margin=dict(l=0, r=30, t=20, b=30),
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

import calendar
from datetime import date, datetime, timedelta

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
    # Filter for current user
    df = df[df["user"] == current_user]

    # Add color column with black color when overdrive==True
    df["color"] = df.apply(
        lambda row: 0 if row["overdrive"] else row["intensity"], axis=1
    )

    # Get the requested section to crop the plot accordingly
    section = request.GET.get("section", None)

    if section == "week":
        start_date = date.today() - timedelta(
            days=date.today().weekday()
        )  # Monday current week
        end_date = start_date + timedelta(days=6)  # Sunday
        title = start_date.strftime("%m/%d/%Y") + " - " + end_date.strftime("%m/%d/%Y")
    elif section == "month":
        start_date = date.today().replace(day=1)
        month_days = calendar.monthrange(start_date.year, start_date.month)[1]
        end_date = start_date.replace(day=month_days)
        title = start_date.strftime("%B") + " " + start_date.strftime("%Y")
    elif section == "year":
        start_date = date.today().replace(month=1, day=1)
        end_date = start_date.replace(month=12, day=31)
        title = start_date.year
    elif section == "all":
        title = "All Time"
    else:  # Month
        start_date = date.today().replace(day=1)
        month_days = calendar.monthrange(start_date.year, start_date.month)[1]
        end_date = start_date.replace(day=month_days)
        title = start_date.strftime("%B") + " " + start_date.strftime("%Y")

    # Creation of the plot
    fig_bar = px.bar(
        df,
        x="date",
        y="intensity",
        title=title,
        labels={"intensity": "Intensity", "date": "Date"},
        color=df["color"],
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
    fig_bar.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="white",
        title_font_family="Jost",
        modebar_orientation="v",
        coloraxis_showscale=False,
        title_x=0.5,
    )
    if section != "all":
        fig_bar.update_xaxes(range=[start_date, end_date])

    bar_chart = fig_bar.to_html(
        full_html=False, include_plotlyjs=False, config={"displayModeBar": False}
    )

    return render(
        request,
        "base/log_plot.html",
        {"bar_chart": bar_chart},
    )

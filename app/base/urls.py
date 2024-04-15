from django.contrib.auth.views import LogoutView
from django.urls import path

from .views import (CustomLoginView, DeleteView, LogCreate, LogDetail, LogList,
                    LogReorder, LogUpdate, RegisterPage, logplot)

urlpatterns = [
    path("login/", CustomLoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(next_page="login"), name="logout"),
    path("register/", RegisterPage.as_view(), name="register"),
    path("", LogList.as_view(), name="logs"),
    path("log-create/", LogCreate.as_view(), name="log-create"),
    path("log-update/<int:pk>/", LogUpdate.as_view(), name="log-update"),
    path("log-delete/<int:pk>/", DeleteView.as_view(), name="log-delete"),
    path("log-plot/", logplot, name="log-plot"),
]

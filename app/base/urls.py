from django.urls import path
from .views import LogList, LogDetail, LogCreate, LogUpdate, DeleteView, CustomLoginView, RegisterPage, LogReorder, logplot
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('register/', RegisterPage.as_view(), name='register'),

    path('', LogList.as_view(), name='logs'),
    path('log/<int:pk>/', LogDetail.as_view(), name='log'),
    path('log-create/', LogCreate.as_view(), name='log-create'),
    path('log-update/<int:pk>/', LogUpdate.as_view(), name='log-update'),
    path('log-delete/<int:pk>/', DeleteView.as_view(), name='log-delete'),
    path('log-reorder/', LogReorder.as_view(), name='log-reorder'),
    path('log-plot/', logplot, name='log-plot')
]

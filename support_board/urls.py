from django.urls import path
from . import views

app_name = 'support_board'

urlpatterns = [
    path('', views.index, name='index'),
]

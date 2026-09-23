from django.urls import path

from . import views

urlpatterns = [path("", views.AskView.as_view(), name="ask")]

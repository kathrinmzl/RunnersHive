# This file is where we'll list our blog app-specific URLs.
from . import views
from django.urls import path

urlpatterns = [
    # Keep slug URLs at the end of the list
    path('', views.EventListView.as_view(), name='events'),
    path('create/', views.EventCreateView.as_view(), name='event_create'),
    path('<slug:slug>/', views.event_detail, name='event_detail')
]
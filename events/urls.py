# This file is where we'll list our blog app-specific URLs.
from . import views
from django.urls import path

urlpatterns = [
    # Urlpattern for EventListView class-based view named events.
    path('', views.EventListView.as_view(), name='events'),

]
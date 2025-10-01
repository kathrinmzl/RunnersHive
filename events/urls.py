"""
URL configuration for the events app.

Maps URLs to views for listing, creating, updating, deleting
and toggling events.
"""

from django.urls import path
from . import views

urlpatterns = [
    # List all future events
    path('', views.EventListView.as_view(), name='events'),

    # Create a new event
    path('create/', views.EventCreateView.as_view(), name='event_create'),

    # User profile with upcoming and past events
    path('profile/', views.ProfileView.as_view(), name='profile'),

    # Event detail page (slugs must be last to avoid conflicts)
    path('<slug:slug>/', views.event_detail, name='event_detail'),

    # Delete an event
    path(
        '<slug:slug>/delete/',
        views.event_delete,
        name='event_delete'
    ),

    # Edit an event
    path(
        '<slug:slug>/edit/',
        views.EventUpdateView.as_view(),
        name='event_edit'
    ),

    # Toggle cancellation status
    path(
        '<slug:slug>/toggle_cancel/',
        views.toggle_event_cancel,
        name='event_cancel'
    ),
]

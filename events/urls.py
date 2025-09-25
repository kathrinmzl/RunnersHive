# This file is where we'll list our blog app-specific URLs.
from . import views
from django.urls import path

urlpatterns = [
    # Keep slug URLs at the end of the list
    path('', views.EventListView.as_view(), name='events'),
    path('create/', views.EventCreateView.as_view(), name='event_create'),
    path('profile/', views.ProfileView.as_view(), name="profile"),
    path('<slug:slug>/', views.event_detail, name='event_detail'),
    path('<slug:slug>/delete/', views.EventDeleteView.as_view(), 
         name='event_delete'),
    path('<slug:slug>/edit/', views.EventUpdateView.as_view(),
         name='event_edit'),
    path('<slug:slug>/toggle_cancel/', views.toggle_event_cancel,
         name='event_cancel')
]

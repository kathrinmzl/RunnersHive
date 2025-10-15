"""
URL configuration for the core app.

Maps URLs for core functionalities like the index and contact pages.
"""

from django.urls import path
from . import views

urlpatterns = [
    # Contact form
    path('contact/', views.contact_view, name='contact'),
]

"""
Configuration for the `events` app.
"""

from django.apps import AppConfig


class EventsConfig(AppConfig):
    """
    AppConfig for the events app.

    Defines the default primary key field type and app name.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'events'

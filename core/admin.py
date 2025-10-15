"""
Django admin configuration for the core app.

Registers the ContactMessage model with custom admin settings.
"""

from django.contrib import admin
from .models import ContactMessage


@admin.register(ContactMessage)
class ContactAdmin(admin.ModelAdmin):
    """
    Admin configuration for ContactMessage model.
    """

    # Columns displayed on the admin list page
    list_display = ("subject", "name", "email", "created_at", "read")

    # Filters shown in the right sidebar
    list_filter = ("created_at", "read")

    # Enable keyword search for quicker message lookup
    search_fields = ("name", "email", "subject", "message")

    # Prevent accidental modification of submission timestamp
    readonly_fields = ("created_at",)

    # Allow marking messages as read directly from the list view
    list_editable = ("read",)

"""
Django admin configuration for the events app.
Registers Event and Category models with custom admin settings.
"""

from django.contrib import admin
from django_summernote.admin import SummernoteModelAdmin
from .models import Event, Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """
    Admin configuration for Category model.

    Allows managing categories in the admin with:
    - Editable sort_order field for manual ordering
    - Name as the clickable link to edit the category
    """
    # Fields displayed in admin list
    list_display = ('name', 'sort_order')

    # Allow editing of sort_order directly
    list_editable = ('sort_order',)

    # Name field clickable for editing
    list_display_links = ('name',)

    # Default ordering in admin list
    ordering = ('sort_order',)


@admin.register(Event)
class EventAdmin(SummernoteModelAdmin):
    """
    Admin configuration for Event model.

    Uses Summernote rich text editor for description.
    Provides search, filtering and list display features.
    """
    # Columns displayed in the admin list page
    list_display = (
        'title', 'organizer', 'date', 'start_time', 'is_past', 'cancelled'
    )

    # Fields that can be searched quickly
    search_fields = ('title', 'organizer', 'location', 'description')

    # Sidebar filters for easy filtering
    list_filter = ('cancelled', 'date', 'difficulty', 'category')

    # Rich text editor for description
    summernote_fields = ('description',)

    # Exclude auto-generated slug from admin form
    exclude = ('slug',)

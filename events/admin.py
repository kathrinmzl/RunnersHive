from django.contrib import admin
from django_summernote.admin import SummernoteModelAdmin
from .models import Event, Category


# Register your models here.
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'sort_order',)  # name first
    list_editable = ('sort_order',)         # sort_order editable
    list_display_links = ('name',)          # name clickable
    ordering = ('sort_order',)


@admin.register(Event)
class EventAdmin(SummernoteModelAdmin):
    # Columns displayed in the Posts list page
    list_display = (
        'title', 'organizer', 'date', 'start_time', 'is_past', 'cancelled'
        )
    # Fields to enable fast search
    search_fields = ('title', 'organizer', 'location', 'description')
    # Sidebar filter for status
    list_filter = ('cancelled', 'date', 'difficulty', 'category')
    # Rich text only for description
    summernote_fields = ('description',)
    # hide slug from admin form because it's auto generated in the model
    exclude = ('slug',)

from django.contrib import admin
from .models import ContactMessage


@admin.register(ContactMessage)
class ContactAdmin(admin.ModelAdmin):
    list_display = ("subject", "name", "email", "created_at", "read")
    list_filter = ("created_at", "read")
    search_fields = ("name", "email", "subject", "message")
    readonly_fields = ("created_at",)
    list_editable = ("read",)

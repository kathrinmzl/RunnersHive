"""
Models for the core app.

Includes:
- ContactMessage: Represents a message submitted via the contact form,
  including sender information, message content, and read status.
"""

from django.db import models
from django.contrib.auth.models import User


class ContactMessage(models.Model):
    """
    Represents a single message submitted through the contact form.

    Stores basic contact details such as the sender's name and email,
    as well as the subject and body of the message itself. Messages can be
    marked as read in the admin interface to assist with inbox management.

    If submitted by an authenticated user, their account is stored in the
    optional `user` field.

    This model is created via :view:`contact_view`.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="contact_messages"
    )

    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """Return a readable label for the event."""
        return f"{self.name} - {self.subject}"

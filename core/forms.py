"""
Forms for the core app.

Includes:
- ContactForm: Model form used to submit messages via the contact page.
"""

from django import forms
from .models import ContactMessage


class ContactForm(forms.ModelForm):
    """
    Form used to collect and submit a contact message.
    """
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control',
                                           'placeholder': 'Your Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control',
                                             'placeholder': 'Your Email'}),
            'subject': forms.TextInput(attrs={'class': 'form-control',
                                              'placeholder': 'Subject'}),
            'message': forms.Textarea(attrs={'class': 'form-control',
                                             'placeholder': 'Your Message',
                                             'rows': 5}),
        }

"""
Forms for the events app.

Includes:
- EventFilterForm: Used to filter Event instances by category, difficulty,
  date, and cancellation status.
- EventForm: Model form for creating or editing Event instances, including
  rich text description and optional media.
"""

from django import forms
from django.utils import timezone
from django_summernote.widgets import SummernoteWidget
from datetime import datetime
from .models import Category, Event


class EventFilterForm(forms.Form):
    """
    Form used to filter events on the frontend by category,
    difficulty, date range, and cancellation status.
    """

    # Allow users to filter by one or more categories
    category = forms.ModelMultipleChoiceField(
        queryset=Category.objects.all(),
        required=False,  # Optional: user doesn't have to pick anything
        widget=forms.CheckboxSelectMultiple  # Display as checkboxes
    )

    # Same approach for difficulty levels
    difficulty = forms.MultipleChoiceField(
        choices=Event.Difficulty.choices,
        required=False,
        widget=forms.CheckboxSelectMultiple
    )

    # Predefined date range filters
    date_filter = forms.ChoiceField(
        choices=[
            ('today', 'Today'),
            ('tomorrow', 'Tomorrow'),
            ('this_week', 'This Week'),
            ('all', 'All')
        ],
        required=False,
        widget=forms.RadioSelect,
        initial='all'  # Preselect "All" by default
    )

    # Simple toggle to hide cancelled events
    cancelled = forms.BooleanField(
        required=False,
        label="Don't Show Cancelled Events",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )


class EventForm(forms.ModelForm):
    """
    Form used to create or edit a running event.

    Includes validation to ensure:
    - The event does not start in the past.
    - The end time occurs after the start time.
    """

    class Meta:
        model = Event
        fields = [
            "title", "organizer", "description", "date",
            "start_time", "end_time", "category", "difficulty",
            "location", "link", "featured_image"
        ]
        widgets = {
            # Enable Summernote editor for better formatting
            "description": SummernoteWidget(),

            # Date and time picker widgets
            "date": forms.DateInput(attrs={
                "type": "date", "class": "form-control"}),
            "start_time": forms.TimeInput(attrs={
                "type": "time", "class": "form-control"}),
            "end_time": forms.TimeInput(attrs={
                "type": "time", "class": "form-control"}),

            # Display category selection as checkboxes
            "category": forms.CheckboxSelectMultiple(),

            # Default Django file input
            "featured_image": forms.ClearableFileInput(attrs={
                "class": "form-control"}),
        }

    def clean(self):
        """
        Perform custom validation on date and time fields.

        Ensures:
        - Event does not start in the past.
        - Start time is before end time.
        """
        cleaned_data = super().clean()
        date = cleaned_data.get("date")
        start_time = cleaned_data.get("start_time")
        end_time = cleaned_data.get("end_time")

        # Ensure the event does not start in the past
        if date and start_time:
            # Merge date and time into a single datetime
            event_dt = datetime.combine(date, start_time)

            # Make timezone-aware so comparison is accurate
            event_dt = timezone.make_aware(
                event_dt, timezone.get_current_timezone())

            if event_dt < timezone.localtime():
                raise forms.ValidationError(
                    "An event cannot start in the past. "
                    "Please check your chosen date and start time."
                )

        # Ensure start time is before end time
        if start_time and end_time:
            if start_time > end_time:
                raise forms.ValidationError(
                    "The end time of the event must be after the start time. "
                    "Please check your chosen times."
                )

        return cleaned_data

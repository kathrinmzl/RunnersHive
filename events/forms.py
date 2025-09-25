from django import forms
from django.utils import timezone
from datetime import datetime
from .models import Category, Event


class EventFilterForm(forms.Form):

    category = forms.ModelMultipleChoiceField(
        queryset=Category.objects.all(),
        required=False,
        # widget=forms.CheckboxSelectMultiple(attrs={'class': 'btn-check'})
        widget=forms.CheckboxSelectMultiple
    )

    difficulty = forms.MultipleChoiceField(
        choices=Event.Difficulty.choices,
        required=False,
        widget=forms.CheckboxSelectMultiple
    )

    date_filter = forms.ChoiceField(
        choices=[
            ('today', 'Today'),
            ('tomorrow', 'Tomorrow'),
            ('this_week', 'This Week'),
            ('all', 'All')
        ],
        required=False,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        initial='all'  # Preselect "All"
    )

    cancelled = forms.BooleanField(
        required=False,
        label="Don't Show Cancelled Events",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = [
            "title", "organizer", "description", "date",
            "start_time", "end_time", "category", "difficulty",
            "location", "link", "featured_image"
        ]
        widgets = {
            "description": forms.Textarea(attrs={
                "rows": 6, "class": "form-control"}),
            "date": forms.DateInput(attrs={
                "type": "date", "class": "form-control"}),
            "start_time": forms.TimeInput(attrs={
                "type": "time", "class": "form-control"}),
            "end_time": forms.TimeInput(attrs={
                "type": "time", "class": "form-control"}),
            "category": forms.CheckboxSelectMultiple(),
            "featured_image": forms.ClearableFileInput(attrs={
                "class": "form-control"}),
        }

    def clean(self):
        cleaned_data = super().clean()
        date = cleaned_data.get("date")
        start_time = cleaned_data.get("start_time")
        end_time = cleaned_data.get("end_time")

        # make sure you cannot submit an event that starts in the past
        if date and start_time:
            # combine date and time into one datetime
            event_dt = datetime.combine(date, start_time)
            # make timezone aware
            event_dt = timezone.make_aware(
                event_dt, timezone.get_current_timezone())

            if event_dt < timezone.localtime():
                raise forms.ValidationError(
                    "An event cannot start in the past.\
                        Please check your chosen date and start time."
                )
        
        # make sure the start time is before the end time
        if start_time and end_time:
            if start_time > end_time:
                raise forms.ValidationError(
                    "The end time of the event has to be after the start time.\
                        Please check your chosen times."
                )

        return cleaned_data

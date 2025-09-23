from django import forms
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
            "description": forms.Textarea(attrs={"rows": 6, "class": "form-control"}),
            "date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "start_time": forms.TimeInput(attrs={"type": "time", "class": "form-control"}),
            "end_time": forms.TimeInput(attrs={"type": "time", "class": "form-control"}),
            "category": forms.CheckboxSelectMultiple(),
            # 🔹 Featured image = File input
            "featured_image": forms.ClearableFileInput(attrs={"class": "form-control"}),
        }


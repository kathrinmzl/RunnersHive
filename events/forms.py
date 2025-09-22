from django import forms
from .models import Category, Event


class EventFilterForm(forms.Form):

    category = forms.ModelMultipleChoiceField(
        queryset=Category.objects.all(),
        required=False,
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

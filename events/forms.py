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

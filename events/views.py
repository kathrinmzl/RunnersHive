from django.shortcuts import render
from django.views.generic import ListView
from datetime import date
from .models import Event, Category
from .forms import EventFilterForm


class EventListView(ListView):
    model = Event
    template_name = "events/event_list.html"
    context_object_name = "events"
    paginate_by = 9

    def get_queryset(self):
        """
        Return only future events (date >= today), ordered by date and
        start_time, filtered by category and difficulty if selected.
        """
        queryset = Event.objects.filter(
            date__gte=date.today()
        ).order_by("date", "start_time")

        # Filtering
        # Instantiate the form with GET data
        self.form = EventFilterForm(self.request.GET or None)
        
        if self.form.is_valid():
            categories = self.form.cleaned_data.get("category")
            difficulties = self.form.cleaned_data.get("difficulty")
            if categories:
                queryset = queryset.filter(category__in=categories).distinct()
            if difficulties:
                queryset = queryset.filter(difficulty__in=difficulties)

        return queryset

    def get_context_data(self, **kwargs):
        """
        Add all categories and difficulties to the context,
        so we can render filter options in the template.
        """
        context = super().get_context_data(**kwargs)
        context["form"] = self.form
        return context


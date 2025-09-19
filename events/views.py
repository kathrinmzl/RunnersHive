from django.shortcuts import render
from django.views.generic import ListView
from datetime import date
from .models import Event

# Create your views here.


class EventListView(ListView):
    model = Event
    template_name = "events/event_list.html"  # your template
    context_object_name = "events"  # how to refer to the list in the template
    paginate_by = 9  # paginate the events list

    def get_queryset(self):
        """
        Return only future events (date >= today) ordered by date and 
        start_time.
        """
        # __gte = "greater than or equal to" lookup
        return Event.objects.filter(
            date__gte=date.today()
        ).order_by("date", "start_time")

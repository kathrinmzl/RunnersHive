from django.shortcuts import render
from django.views.generic import ListView
from datetime import date, timedelta
from urllib.parse import urlencode
from .models import Event, Category
from .forms import EventFilterForm

# https://bastakiss.com/blog/django-6/enhancing-django-listview-with-dynamic-filtering-a-step-by-step-guide-403

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
            # Category
            categories = self.form.cleaned_data.get("category")
            if categories:
                queryset = queryset.filter(category__in=categories).distinct()
            
            # Difficulty
            difficulties = self.form.cleaned_data.get("difficulty")
            if difficulties:
                queryset = queryset.filter(difficulty__in=difficulties)

            # Date
            date_filter = self.form.cleaned_data.get('date_filter')
            today = date.today()
            if date_filter == 'today':
                queryset = queryset.filter(date=today)
            elif date_filter == 'tomorrow':
                queryset = queryset.filter(date=today + timedelta(days=1))
            elif date_filter == 'this_week':
                # Assuming week starts on Monday
                start_of_week = today - timedelta(days=today.weekday())
                end_of_week = start_of_week + timedelta(days=6)
                queryset = queryset.filter(date__range=[start_of_week, end_of_week])
            # 'all' -> no date filter

        return queryset

    def get_context_data(self, **kwargs):
        """
        Add all categories and difficulties to the context,
        so we can render filter options in the template.
        """
        context = super().get_context_data(**kwargs)
        context["form"] = self.form

        # Preserve filter params in pagination links
        query_params = self.request.GET.copy()
        if "page" in query_params:
            query_params.pop("page")  # remove current page if exists
        context["query_string"] = query_params.urlencode()

        return context


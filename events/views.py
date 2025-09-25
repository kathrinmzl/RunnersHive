from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from datetime import date, timedelta, datetime
from .models import Event
from .forms import EventFilterForm, EventForm


# https://bastakiss.com/blog/django-6/enhancing-django-listview-with-dynamic-filtering-a-step-by-step-guide-403


class TodaysEventsListView(ListView):
    model = Event
    template_name = "index.html"
    context_object_name = "todays_events"
    paginate_by = 6

    # Return only todays events, ordered by start_time
    queryset = Event.objects.filter(
        date=date.today()
    ).order_by("start_time")


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
                queryset = queryset.filter(
                    date__range=[start_of_week, end_of_week]
                    )
            # 'all' -> no date filter

            # Cancelled filter
            exclude_cancelled = self.form.cleaned_data.get("cancelled")
            if exclude_cancelled:
                queryset = queryset.filter(cancelled=False)

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


def event_detail(request, slug):
    """
    Display an individual :model:`events.Event`.

    **Context**

    ``event``
        An instance of :model:`events.Event`.

    **Template:**

    :template:`events/event_detail.html`
    """
    queryset = queryset = Event.objects
    # queryset = queryset = Event.objects.filter(
    #         date__gte=date.today()
    #     )
    # get one post returned with that unique slug or an error message if slug doesnt exist
    event = get_object_or_404(queryset, slug=slug)

    # print("About to render template")
    return render(  # returns an HttpResponse
        request,
        "events/event_detail.html",
        {
            "event": event
        },  # dict with the data -> available for use in the
        # template as the DTL variable e.g. {{ event }}
    )


class EventCreateView(LoginRequiredMixin, CreateView):
    model = Event
    form_class = EventForm
    template_name = "events/event_form.html"
    success_url = reverse_lazy("events")

    def form_valid(self, form):
        # assign logged-in user as author
        form.instance.author = self.request.user
        # Success message
        messages.add_message(
            self.request, messages.SUCCESS,
            'Event created successfully'
        )
        return super().form_valid(form)


class ProfileView(LoginRequiredMixin, ListView):
    template_name = "events/profile.html"
    paginate_by = 9
    context_object_name = 'upcoming_events'

    def get_queryset(self):
        # Fetch all events of the user
        all_events = Event.objects.filter(author=self.request.user)
        # Filter using the is_past property
        upcoming = [e for e in all_events if not e.is_past]
        # Sort by date + start_time
        upcoming.sort(key=lambda e: datetime.combine(e.date, e.start_time))
        return upcoming

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Fetch past events for display (no pagination)
        all_events = Event.objects.filter(author=self.request.user)
        past_events = [e for e in all_events if e.is_past]
        past_events.sort(key=lambda e: 
                         datetime.combine(e.date, e.start_time), reverse=True)
        context['past_events'] = past_events

        return context


class EventUpdateView(LoginRequiredMixin, UpdateView):
    model = Event
    form_class = EventForm
    template_name = "events/event_form.html"  # same as create
    context_object_name = "event"

    def get_queryset(self):
        # Only allow editing of events the user owns
        return Event.objects.filter(author=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, "Event updated successfully!")
        return super().form_valid(form)

    def get_success_url(self):
        # Redirect to event detail page
        return reverse("profile")


class EventDeleteView(LoginRequiredMixin, DeleteView):
    model = Event
    success_url = reverse_lazy("profile")  # redirect to profile
    context_object_name = "event"

    def get_queryset(self):
        # Users can only delete their own events
        return Event.objects.filter(author=self.request.user)

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Event deleted successfully!")
        return super().delete(request, *args, **kwargs)


@login_required
def toggle_event_cancel(request, slug):
    # Fetch the event belonging to the logged-in user
    event = get_object_or_404(Event, slug=slug, author=request.user)

    # Only allow this action if its a POST request
    if request.method == "POST":
        # Toggle the current "cancelled" state
        event.cancelled = not event.cancelled
        event.save()

        # Success message depending on new status
        if event.cancelled:
            messages.warning(request,
                             f"Event '{event.title}' has been cancelled.")
        else:
            messages.success(request,
                             f"Event '{event.title}' is active again.")

    # Redirect user back to profile
    return redirect("profile")

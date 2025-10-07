"""
Views for the events app.

Includes:
- Class-based views for listing, creating, updating, and deleting events
- Function-based views for event detail, deletion, and toggling cancel status
- Context and filtering logic for events
"""

from datetime import timedelta, datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.views.generic import ListView, CreateView, UpdateView
from .models import Event
from .forms import EventFilterForm, EventForm


class TodaysEventsListView(ListView):
    """
    Display today's upcoming events on the homepage.

    **Context:**

    ``todays_events``
        List of Event instances happening today and not past yet.

    **Template:** :template:`index.html`
    """
    model = Event
    template_name = "index.html"
    context_object_name = "todays_events"
    paginate_by = 6

    def get_queryset(self):
        """
        Return events happening today that have not already ended.
        """
        todays_events = Event.objects.filter(
            date=timezone.localdate()
        ).order_by("start_time")
        todays_upcoming_events = [e for e in todays_events if not e.is_past]
        return todays_upcoming_events


# Extending ListView for Filtering see:
# https://bastakiss.com/blog/django-6/enhancing-django-listview-with-dynamic-
# filtering-a-step-by-step-guide-403
class EventListView(ListView):
    """
    Display a paginated list of future events with filter options.

    **Context:**

    ``events``
        List of future Event instances filtered by GET params.
    ``form``
        Instance of EventFilterForm to render filter inputs.
    ``query_string``
        URL-encoded GET parameters for preserving filters in pagination.

    **Template:** :template:`events/event_list.html`
    """
    model = Event
    template_name = "events/event_list.html"
    context_object_name = "events"
    paginate_by = 9

    def get_queryset(self):
        """
        Return future events filtered by category, difficulty, date,
        and cancellation status. Excludes events already in the past.
        """
        today = timezone.localdate()
        queryset = Event.objects.filter(
            date__gte=today
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

        # Exclude events that are already past
        queryset = [e for e in queryset if not e.is_past]
        return queryset

    def get_context_data(self, **kwargs):
        """
        Add the filter form and preserved GET parameters to the context.
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
    Display a single :model:`events.Event` by slug.

    **Context:**

    ``event``
        Instance of Event corresponding to the slug.

    **Template:** :template:`events/event_detail.html`
    """
    queryset = Event.objects
    event = get_object_or_404(queryset, slug=slug)

    return render(
        request,
        "events/event_detail.html",
        {"event": event},
    )


class EventCreateView(LoginRequiredMixin, CreateView):
    """
    Allow logged-in users to create a new event.

    **Template:** :template:`events/event_form.html`
    """
    model = Event
    form_class = EventForm
    template_name = "events/event_form.html"

    def form_valid(self, form):
        """
        Set the logged-in user as author of the event and display a success
        message.
        """
        form.instance.author = self.request.user
        response = super().form_valid(form)
        messages.success(
            self.request,
            f"Event '{form.instance.title}' created successfully!"
        )
        return response

    def form_invalid(self, form):
        """
        Display an error message if event creation fails.
        """
        # Get the title from form data if it's available
        title = (
            form.cleaned_data.get('title')
            if 'title' in form.cleaned_data
            else 'Untitled Event'
        )
        messages.error(
            self.request,
            f"Could not create event '{title}'. Please check your input."
        )
        return super().form_invalid(form)

    def get_success_url(self):
        """Return the URL of the newly created event's detail page."""
        return reverse("event_detail", args=[self.object.slug])


class ProfileView(LoginRequiredMixin, ListView):
    """
    Display upcoming and past events of the logged-in user.

    **Context:**

    ``upcoming_events``
        Paginated list of user's upcoming events.
    ``past_events``
        List of user's past events (not paginated).

    **Template:** :template:`events/profile.html`
    """
    template_name = "events/profile.html"
    paginate_by = 9
    context_object_name = 'upcoming_events'

    def get_queryset(self):
        """
        Return a sorted list of upcoming events for the logged-in user.
        """
        all_events = Event.objects.filter(author=self.request.user)
        upcoming = [e for e in all_events if not e.is_past]
        upcoming.sort(key=lambda e: datetime.combine(e.date, e.start_time))
        return upcoming

    def get_context_data(self, **kwargs):
        """
        Add past events to the context for display.
        """
        context = super().get_context_data(**kwargs)
        all_events = Event.objects.filter(author=self.request.user)
        past_events = [e for e in all_events if e.is_past]
        past_events.sort(
            key=lambda e: datetime.combine(e.date, e.start_time),
            reverse=True
        )
        context['past_events'] = past_events
        return context


class EventUpdateView(LoginRequiredMixin, UpdateView):
    """
    Allow users to update their own events.

    **Template:** :template:`events/event_form.html`
    """
    model = Event
    form_class = EventForm
    template_name = "events/event_form.html"
    context_object_name = "event"

    def get_queryset(self):
        """Return events belonging to the logged-in user."""
        return Event.objects.filter(author=self.request.user)

    def dispatch(self, *args, **kwargs):
        """
        Prevent editing past events or events not owned by the user.

        If the event is in the past, an info message is shown and the user is
        redirected to the previous page or to the profile page. If the event
        does not belong to the logged-in user, an error message is shown and
        the user is redirected similarly. Non-existent events also redirect
        with an error message.
        """
        try:
            event = Event.objects.get(slug=kwargs['slug'])
        except Event.DoesNotExist:
            messages.error(self.request, "Event not found.")
            return redirect("profile")

        if event.author != self.request.user:
            messages.error(self.request,
                           "You do not have permission to edit this event.")
            return redirect(self.request.META.get('HTTP_REFERER', 'profile'))

        if event.is_past:
            messages.info(self.request,
                          f"Event '{event.title}' is in the past! You cannot "
                          "edit it anymore.")
            return redirect(self.request.META.get('HTTP_REFERER', 'profile'))

        return super().dispatch(self.request, *args, **kwargs)

    def form_valid(self, form):
        """Save updated event and show a success message."""
        response = super().form_valid(form)
        messages.success(
            self.request,
            f"Event '{form.instance.title}' updated successfully!"
        )
        return response

    def form_invalid(self, form):
        """Show an error message if update fails."""
        title = (
            form.cleaned_data.get('title')
            if 'title' in form.cleaned_data
            else 'Untitled Event'
        )
        messages.error(
            self.request,
            f"Could not update event '{title}'. Please check your input."
        )
        return super().form_invalid(form)

    def get_success_url(self):
        """Return the URL of the updated event's detail page."""
        return reverse("event_detail", args=[self.object.slug])


@login_required
def event_delete(request, slug):
    """
    Delete a single event belonging to the logged-in user.

    **Template:** Redirects to profile page

    Shows a success or error message using Django messages.
    """
    event = get_object_or_404(Event, slug=slug, author=request.user)

    if request.method == "POST":
        event.delete()
        messages.success(
            request, f"Event '{event.title}' deleted successfully!"
        )
        return redirect("profile")

    # Redirect to profile if GET request or any other method
    messages.error(
        request,
        f"Event '{event.title}' could not be deleted. Invalid request method."
    )
    return redirect("profile")


@login_required
def toggle_event_cancel(request, slug):
    """
    Toggle the 'cancelled' status of an event belonging to the logged-in user.

    **Template:** Redirects to profile page

    Shows success or error messages depending on the action.
    """
    event = get_object_or_404(Event, slug=slug, author=request.user)

    if request.method == "POST":
        event.cancelled = not event.cancelled
        event.save()
        if event.cancelled:
            messages.warning(
                request, f"Event '{event.title}' has been cancelled."
            )
        else:
            messages.success(
                request, f"Event '{event.title}' is active again."
            )
        return redirect("profile")

    messages.error(
        request,
        f"Cancellation status of event '{event.title}' could not be changed."
    )
    return redirect("profile")

"""
Tests for the events app views.
"""

from datetime import timedelta, time
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import User
from events.models import Event, Category


class EventViewsTestCase(TestCase):
    def setUp(self):
        # Users
        self.user = User.objects.create_user(
            username="testuser", password="password123"
        )
        self.other_user = User.objects.create_user(
            username="otheruser", password="password123"
        )

        # Categories
        self.category1 = Category.objects.create(name="Trail Run")
        self.category2 = Category.objects.create(name="Social Run")

        # Dates
        self.today = timezone.localdate()
        self.tomorrow = self.today + timedelta(days=1)
        self.yesterday = self.today - timedelta(days=1)

        # Events
        self.future_event = Event.objects.create(
            title="Future Event",
            organizer="Organizer A",
            description="Future event description",
            date=self.tomorrow,
            start_time=time(10, 0),
            end_time=time(12, 0),
            difficulty=Event.Difficulty.BEGINNER,
            location="Park",
            author=self.user,
        )
        self.future_event.category.add(self.category1)

        self.past_event = Event.objects.create(
            title="Past Event",
            organizer="Organizer C",
            description="Past event description",
            date=self.yesterday,
            start_time=time(10, 0),
            end_time=time(12, 0),
            difficulty=Event.Difficulty.ADVANCED,
            location="Stadium",
            author=self.user,
        )
        self.past_event.category.add(self.category1)

        # Event today but already past (early morning)
        self.today_past_event = Event.objects.create(
            title="Today Past Event",
            organizer="Organizer B",
            description="Event earlier today",
            date=self.today,
            start_time=time(1, 0),  # 1 AM
            end_time=time(2, 0),    # 2 AM
            difficulty=Event.Difficulty.BEGINNER,
            location="Local Track",
            author=self.user,
        )
        self.today_past_event.category.add(self.category1)

        # Event today that is still upcoming
        self.today_upcoming_event = Event.objects.create(
            title="Today Upcoming Event",
            organizer="Organizer E",
            description="Upcoming today",
            date=self.today,
            start_time=time(22, 0),
            end_time=time(23, 0),
            difficulty=Event.Difficulty.BEGINNER,
            location="Park",
            author=self.user,
        )
        self.today_upcoming_event.category.add(self.category1)

        # Future event that is cancelled
        self.future_cancelled_event = Event.objects.create(
            title="Cancelled Future Event",
            organizer="Organizer D",
            description="Future event but cancelled",
            date=self.tomorrow,
            start_time=time(14, 0),
            end_time=time(16, 0),
            difficulty=Event.Difficulty.INTERMEDIATE,
            location="Gym",
            author=self.user,
            cancelled=True
        )
        self.future_cancelled_event.category.add(self.category2)

        # Other user's event
        self.other_users_event = Event.objects.create(
            title="Other User Event",
            organizer="Other Organizer",
            description="Other user's event",
            date=self.tomorrow,
            start_time=time(9, 0),
            end_time=time(11, 0),
            difficulty=Event.Difficulty.INTERMEDIATE,
            location="Gym",
            author=self.other_user,
        )
        self.other_users_event.category.add(self.category2)

    # ------------------------------
    # TodaysEventsListView
    # ------------------------------
    def test_todays_events_list_view(self):
        """
        Test that TodaysEventsListView only includes events happening today
        and that are not already past.
        """
        url = reverse("home")  # Homepage URL
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # Ensure the context variable exists
        self.assertIn("todays_events", response.context)
        todays_events = response.context["todays_events"]

        # Past event today should NOT appear
        self.assertNotIn(self.today_past_event, todays_events)

        # Upcoming event today SHOULD appear
        self.assertIn(self.today_upcoming_event, todays_events)

        # Future event tomorrow should NOT appear
        self.assertNotIn(self.future_event, todays_events)

    # ------------------------------
    # EventListView
    # ------------------------------
    def test_events_list_view(self):
        """
        Test that the main events list view only includes events that have not
        already ended (i.e., not in the past) and that the view renders
        successfully.
        """
        url = reverse("events")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("events", response.context)

        # Ensure all events in the context are not past events
        for event in response.context["events"]:
            self.assertFalse(event.is_past)

    def test_event_list_view_filter_by_category(self):
        """
        Test filtering the events list by a specific category.

        Only events containing the selected category should appear.
        """
        url = reverse("events")

        # Send GET request with category filter applied
        response = self.client.get(url, {"category": [self.category2.id]})

        # Ensure the request succeeds
        self.assertEqual(response.status_code, 200)

        # All returned events should include the selected category
        for event in response.context["events"]:
            self.assertIn(self.category2, event.category.all())

    def test_event_list_view_filter_by_difficulty(self):
        """
        Test filtering the events list by difficulty level.

        Only events matching the selected difficulty should appear.
        """
        url = reverse("events")

        # Send GET request with difficulty filter applied
        response = self.client.get(
            url, {"difficulty": [Event.Difficulty.BEGINNER]}
            )

        # Ensure the request succeeds
        self.assertEqual(response.status_code, 200)

        # Verify all returned events match the requested difficulty
        for event in response.context["events"]:
            self.assertEqual(event.difficulty, Event.Difficulty.BEGINNER)

    def test_event_list_view_exclude_cancelled(self):
        """
        Test that events marked as cancelled are excluded when the 'exclude
        cancelled' filter is applied.
        """
        # Mark one event as cancelled
        self.future_event.cancelled = True
        self.future_event.save()

        url = reverse("events")
        # Form param to exclude cancelled
        response = self.client.get(url, {"cancelled": "on"})
        self.assertEqual(response.status_code, 200)

        # Ensure all events in the context are not cancelled
        for event in response.context["events"]:
            self.assertFalse(event.cancelled)

    # ------------------------------
    # event_detail view
    # ------------------------------
    def test_event_detail_view(self):
        """
        Test that the event_detail view correctly retrieves a single event
        by its slug and renders the detail template successfully.
        """
        # Reverse the URL for the event_detail view using the slug of a
        # future event
        url = reverse("event_detail", args=[self.future_event.slug])

        # Perform a GET request to the detail page
        response = self.client.get(url)

        # Check that the view returns HTTP 200 (OK)
        self.assertEqual(response.status_code, 200)

        # Ensure that the 'event' context variable exists and contains the
        # correct Event instance
        self.assertEqual(response.context["event"], self.future_event)

    # ------------------------------
    # EventCreateView
    # ------------------------------
    def test_create_event_requires_login(self):
        """
        Test that accessing the event creation page requires a logged-in user.

        Anonymous users should be redirected to the login page.
        """
        # Generate URL for the event creation view
        url = reverse("event_create")

        # Perform GET request without logging in
        response = self.client.get(url)

        # Assert that response is a redirect (HTTP 302) to the login page
        self.assertEqual(response.status_code, 302)

        # The login redirect should include '?next=<original_url>'
        login_url = reverse("account_login")
        self.assertRedirects(response, f"{login_url}?next={url}")

    def test_create_event_post_by_owner(self):
        """
        Test that a logged-in user can successfully create a new event via
        POST.

        The event should be saved in the database, and the response should
        redirect
        to the event's detail page.
        """
        # Log in as the test user
        self.client.login(username="testuser", password="password123")

        # Generate URL for the event creation view
        url = reverse("event_create")

        # Prepare POST data for the new event
        data = {
            "title": "New Event",
            "organizer": "Organizer A",
            "description": "Test event",
            "date": self.tomorrow,
            "start_time": "10:00",
            "end_time": "12:00",
            "difficulty": Event.Difficulty.BEGINNER,
            "location": "Park",
            "category": [self.category1.id],  # Many-to-many categories
        }

        # Submit POST request to create the event
        response = self.client.post(url, data)

        # Assert that the response is a redirect (HTTP 302) to the detail page
        self.assertRedirects(
            response, reverse("event_detail",
                              args=[Event.objects.get(title="New Event").slug])
                              )

        # Verify that the event was actually created in the database
        self.assertTrue(Event.objects.filter(title="New Event").exists())

    # ------------------------------
    # ProfileView
    # ------------------------------
    def test_profile_view_contains_upcoming_and_past_events(self):
        """
        Test that the profile view for a logged-in user correctly provides:
        - 'upcoming_events': a list of the user's future events
        - 'past_events': a list of the user's past events

        The response should render successfully and include both context
        variables.
        """
        # Log in as the test user
        self.client.login(username="testuser", password="password123")

        # Generate URL for the profile view
        url = reverse("profile")

        # Perform GET request
        response = self.client.get(url)

        # Assert that the response renders successfully (HTTP 200)
        self.assertEqual(response.status_code, 200)

        # Ensure that the context contains the 'upcoming_events' and
        # 'past_events' variables
        self.assertIn("upcoming_events", response.context)
        self.assertIn("past_events", response.context)

        upcoming_events = response.context["upcoming_events"]
        past_events = response.context["past_events"]

        # Known events should appear in the correct lists
        self.assertIn(self.future_event, upcoming_events)
        self.assertIn(self.past_event, past_events)

        # Ensure no past events are in upcoming_events
        for event in upcoming_events:
            self.assertFalse(event.is_past,
                             f"Past event '{event.title}'\
                                should not appear in upcoming_events")

        # Ensure no upcoming events are in past_events
        for event in past_events:
            self.assertTrue(event.is_past,
                            f"Future event '{event.title}'\
                                should not appear in past_events")

    # ------------------------------
    # EventUpdateView
    # ------------------------------
    def test_edit_future_event_by_owner_allowed(self):
        """
        Test that the owner of a future event can successfully update it.

        Checks:
        - Logged-in user can access the update view
        - Event title is updated in the database
        - HTTP response redirects (status 302) to event detail page
        """
        # Log in as the owner
        self.client.login(username="testuser", password="password123")

        # Reverse URL for the edit view
        url = reverse("event_edit", args=[self.future_event.slug])

        # POST updated data to the form
        data = {
            "title": "Future Event Updated",
            "organizer": "Organizer A",
            "description": "Updated desc",
            "date": self.future_event.date,
            "start_time": "10:00",
            "end_time": "12:00",
            "difficulty": Event.Difficulty.BEGINNER,
            "location": "Park",
            "category": [self.category1.id],
        }
        response = self.client.post(url, data)

        # Refresh from database to get latest changes
        self.future_event.refresh_from_db()

        # Check that the event was updated
        self.assertEqual(self.future_event.title, "Future Event Updated")

        # Assert that the response is a redirect (HTTP 302) to the detail page
        self.assertRedirects(
            response, reverse("event_detail",
                              args=[Event.objects.get(
                                  title="Future Event Updated").slug])
                              )

    def test_edit_past_event_by_owner_prevented(self):
        """
        Test that the owner cannot edit a past event.

        Checks:
        - GET request redirects (status 302) since editing past events is
        forbidden
        - Event title remains unchanged in the database
        """
        self.client.login(username="testuser", password="password123")

        url = reverse("event_edit", args=[self.past_event.slug])
        response = self.client.get(url)

        # Past events cannot be edited; expect redirect
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("profile"))

        # Ensure event title is unchanged
        self.past_event.refresh_from_db()
        self.assertEqual(self.past_event.title, "Past Event")

    def test_edit_event_by_non_owner_prevented(self):
        """
        Test that a user cannot edit an event they do not own.

        Checks:
        - GET request redirects (status 302) for non-owners
        - Event remains unchanged in the database
        """
        self.client.login(username="testuser", password="password123")

        url = reverse("event_edit", args=[self.other_users_event.slug])
        response = self.client.get(url)

        # Non-owner cannot edit; expect redirect
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("profile"))

        # Ensure event title is unchanged
        self.other_users_event.refresh_from_db()
        self.assertEqual(self.other_users_event.title, "Other User Event")

    # ------------------------------
    # event_delete View
    # ------------------------------
    def test_delete_future_event_by_owner_allowed(self):
        """
        Test that the event owner can delete a future event.

        Checks:
        - Logged-in owner can successfully send a POST request to delete their
        event
        - HTTP response redirects (status 302) after deletion
        - Event is removed from the database
        """
        # Log in as event owner
        self.client.login(username="testuser", password="password123")

        # Reverse the delete URL for the future event
        url = reverse("event_delete", args=[self.future_event.slug])

        # Send POST request (deletions are only handled via POST)
        response = self.client.post(url)

        # Expect redirect after successful deletion
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("profile"))

        # Confirm event is no longer in the database
        with self.assertRaises(Event.DoesNotExist):
            Event.objects.get(id=self.future_event.id)

    def test_delete_past_event_by_owner_allowed(self):
        """
        Test that the event owner can delete a past event.

        Checks:
        - POST request from the owner succeeds
        - Event is removed from the database
        - Response redirects after deletion
        """
        self.client.login(username="testuser", password="password123")

        url = reverse("event_delete", args=[self.past_event.slug])
        response = self.client.post(url)

        # Expect redirect after deletion
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("profile"))

        # Ensure event was successfully deleted
        with self.assertRaises(Event.DoesNotExist):
            Event.objects.get(id=self.past_event.id)

    def test_delete_event_by_non_owner_prevented(self):
        """
        Test that users cannot delete events they do not own.

        Checks:
        - Non-owner POST request does not delete the event
        - Event remains in the database unchanged
        - Returns a redirect (302) to 'profile' page
        """
        self.client.login(username="testuser", password="password123")

        url = reverse("event_delete", args=[self.other_users_event.slug])
        response = self.client.post(url)

        # Ensure response redirects (usually a failed permission check)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("profile"))

        # Confirm event still exists and was not modified
        self.other_users_event.refresh_from_db()
        self.assertEqual(self.other_users_event.title, "Other User Event")

    # ------------------------------
    # toggle_event_cancel View
    # ------------------------------
    def test_toggle_cancel_future_event_by_owner(self):
        """
        Test that the owner of a future event can successfully toggle its
        'cancelled' status.

        POST request should set `cancelled=True` and redirect (HTTP 302) to
        profile.
        """
        # Log in as the event owner
        self.client.login(username="testuser", password="password123")

        # Reverse URL for the toggle_cancel view
        url = reverse("event_cancel", args=[self.future_event.slug])

        # Perform POST request to toggle cancellation
        response = self.client.post(url)

        # Refresh from DB to get updated values
        self.future_event.refresh_from_db()

        # The event should now be cancelled
        self.assertTrue(self.future_event.cancelled)

        # POST should redirect (302) to profile
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("profile"))

    def test_toggle_cancel_future_event_already_cancelled(self):
        """
        Test toggling the cancellation status of a future event that is
        already cancelled.

        - The 'cancelled' field should flip from True to False.
        - The owner should receive a success message indicating the event
        is active again.
        - POST request should redirect to the profile page.
        """
        self.client.login(username="testuser", password="password123")

        # Confirm initial status
        self.assertTrue(self.future_cancelled_event.cancelled)

        # POST to toggle_cancel
        url = reverse("event_cancel", args=[self.future_cancelled_event.slug])
        response = self.client.post(url)

        # Refresh from DB to get updated value
        self.future_cancelled_event.refresh_from_db()

        # Status should now be active (not cancelled)
        self.assertFalse(self.future_cancelled_event.cancelled)

        # Response should redirect to profile page
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("profile"))

        # Success message should indicate event is active again
        messages_list = list(response.wsgi_request._messages)
        self.assertTrue(any(
            "is active again" in str(m) for m in messages_list))

    def test_toggle_cancel_past_event_prevented(self):
        """
        Ensure that cancelling a past event is explicitly prevented.

        - The 'cancelled' field should remain unchanged (False).
        - The user is redirected to the profile page.
        - An info message is added explaining why cancellation is not allowed.
        """
        self.client.login(username="testuser", password="password123")

        # Attempt to POST to toggle_cancel on a past event
        response = self.client.post(reverse("event_cancel",
                                            args=[self.past_event.slug]))

        # Redirect response to profile page
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("profile"))

        # Event's cancelled status should remain unchanged
        self.past_event.refresh_from_db()
        self.assertFalse(self.past_event.cancelled)

        # Confirm an info message is in the messages framework
        messages_list = list(response.wsgi_request._messages)
        self.assertTrue(any(
            "Cannot change cancellation status" in str(m)
            for m in messages_list))

    def test_toggle_cancel_by_non_owner_prevented(self):
        """
        Test that a user who does not own the event cannot toggle cancellation.
        - Event's 'cancelled' status remains unchanged.
        - Redirects to profile with an error message.
        """
        self.client.login(username="testuser", password="password123")
        url = reverse("event_cancel", args=[self.other_users_event.slug])

        # POST request to toggle
        response = self.client.post(url)

        # Event status should remain unchanged
        self.other_users_event.refresh_from_db()
        self.assertFalse(self.other_users_event.cancelled)

        # Should redirect to profile page
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("profile"))

        # Error message should be present
        messages_list = list(response.wsgi_request._messages)
        self.assertTrue(
            any("not allowed" in str(m) for m in messages_list)
        )

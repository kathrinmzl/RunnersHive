"""
Tests for the core app views.
"""

from django.test import TestCase
from django.urls import reverse
from django.contrib.messages import get_messages
from core.models import ContactMessage


class ContactViewTestCase(TestCase):

    def setUp(self):
        self.url = reverse("contact")

    def test_get_request_renders_form(self):
        """
        Test that accessing the contact page via GET displays the contact form.

        The response should return status code 200, use the correct template,
        and include `contact_form` in the context so that the form renders
        properly on the page.
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "core/contact.html")
        self.assertIn("contact_form", response.context)

    def test_post_valid_data_creates_contact_and_redirects(self):
        """
        Test that submitting a valid contact form via POST creates a
        new ContactMessage object.

        After submission:
        - The view should save the message to the database,
        - Add a success message,
        - And redirect the user back to the homepage.
        """
        data = {
            "name": "Test User",
            "email": "test@example.com",
            "subject": "Test Subject",
            "message": "This is a test message."
        }
        response = self.client.post(self.url, data)

        # Assert that the response redirects to home (HTTP 302)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("home"))

        # Verify that the contact entry was saved to the database
        self.assertTrue(ContactMessage.objects.filter(email="test@example.com")
                        .exists())

        # Confirm that a success message was added to the message framework
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("Thank you!" in str(m) for m in messages))

    def test_post_invalid_data_shows_error_message(self):
        """
        Test that submitting invalid form data does not create a ContactMessage
        entry.

        Instead, the view should:
        - Re-render the contact form (response 200),
        - Display an error message,
        - And leave the database unchanged.
        """
        data = {
            "name": "",  # invalid because name is required
            "email": "not-an-email",  # invalid email format
            "subject": "",
            "message": ""
        }
        response = self.client.post(self.url, data)

        # Assert that the view renders the form again instead of redirecting
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "core/contact.html")

        # Ensure no ContactMessage objects were created
        self.assertFalse(ContactMessage.objects.exists())

        # Confirm an error message was sent
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("could not be sent" in str(m) for m in messages))

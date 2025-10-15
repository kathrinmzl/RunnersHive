"""
Views for the core app.

Includes:
- Function-based view for displaying and processing the contact form
"""

from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import ContactForm


def contact_view(request):
    """
    Display the contact form and process submissions.

    Handles both GET and POST requests:

    - **GET request:**
      Renders an empty `ContactForm` for the user to fill out.

    - **POST request:**
      Validates and saves the submitted message as a `ContactMessage`.
      On success, the user is redirected to the homepage with a success
      message.
      If validation fails, an error message is displayed and the form is
      re-rendered
      with the provided input preserved.

    **Template:** :template:`core/contact.html`

    **Context:**

    ``contact_form``
        Instance of `ContactForm` for rendering in the template.
    """
    if request.method == "POST":
        contact_form = ContactForm(request.POST)
        if contact_form.is_valid():
            contact_form.save()
            messages.success(request, "Thank you! Your message has been sent.")
            return redirect("home")  # Redirect to homepage after submission
        else:
            messages.error(
                request,
                "Your message could not be sent. Please check your input."
            )
    else:
        contact_form = ContactForm()

    return render(request, "core/contact.html", {"contact_form": contact_form})

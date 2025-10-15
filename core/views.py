from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import ContactForm


def contact_view(request):
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

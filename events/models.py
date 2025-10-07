"""
Models for the events app.

Includes:
- Event: Represents a running event with details like date, time,
  categories, difficulty, location, and optional media.
- Category: Represents a category for filtering and organizing events.
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from cloudinary.models import CloudinaryField
from datetime import datetime
from django.utils import timezone


class Category(models.Model):
    """
    Represents a category for organizing running events
    (e.g. Social Run, Trail Run).

    Categories can be managed and ordered in the admin panel and are used
    for filtering events on the frontend.

    This model is used in a Many-to-Many relation with :model:`Event`.
    """

    name = models.CharField(max_length=50)
    # Determines custom ordering of categories in dropdowns and listings
    sort_order = models.PositiveIntegerField(
        default=0, blank=False, null=False
        )

    class Meta:
        # Order categories by sort_order, then by name as fallback
        ordering = ['sort_order', 'name']

    def __str__(self):
        """Return the category name as its string representation."""
        return self.name


class Event(models.Model):
    """
    Represents a single running event created by a user.

    Includes details such as title, date, time, categories, difficulty,
    location and optional media or external links.

    The model is related to :model:`auth.User`
    and :model:`Category`.
    """

    class Difficulty(models.TextChoices):
        BEGINNER = "BEGINNER", "Beginner friendly"
        INTERMEDIATE = "INTERMEDIATE", "Intermediate"
        ADVANCED = "ADVANCED", "Advanced"

    title = models.CharField(max_length=100, unique=True)
    # Allow blank so save() can auto-generate the slug
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    organizer = models.CharField(max_length=40)
    description = models.TextField()
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()

    # Many-to-many relationship: One event can have many categories
    # and a category can belong to many events
    category = models.ManyToManyField(Category, related_name="events")

    difficulty = models.CharField(
        max_length=20, choices=Difficulty.choices, null=True
    )
    location = models.CharField(max_length=100)

    # Optional link to external event page
    link = models.URLField(blank=True, null=True)

    # Optional featured image stored in Cloudinary
    featured_image = CloudinaryField(
        'image', default='placeholder', blank=True, null=True
    )

    cancelled = models.BooleanField(default=False)

    # The user who created the event
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="events"
    )

    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        # Order events chronologically
        ordering = ["date", "start_time"]

    def __str__(self):
        """Return a readable label for the event."""
        return f"{self.title} | Organized by {self.organizer}"

    @property
    def is_past(self):
        """
        Returns True if the event's date and end_time are in the past.
        """
        # Combine date and end_time into a single datetime
        event_dt = datetime.combine(self.date, self.end_time)

        # Convert to timezone-aware datetime for accurate comparison
        event_dt = timezone.make_aware(
            event_dt, timezone.get_current_timezone()
        )

        return event_dt < timezone.localtime()

    def save(self, *args, **kwargs):
        """
        Automatically generate a unique slug using `<title>-<YYYY-MM-DD>`
        if no slug is manually provided.
        """
        if not self.slug:
            date_str = self.date.strftime("%Y-%m-%d")
            self.slug = slugify(f"{self.title}-{date_str}")

        super().save(*args, **kwargs)

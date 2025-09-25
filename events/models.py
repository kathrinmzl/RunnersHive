from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from cloudinary.models import CloudinaryField
from datetime import datetime
from django.utils import timezone


# Create your models here.
class Category(models.Model):
    """
    Represents a category for running events (e.g., Social Run, Trail Run).

    Categories are used for filtering events on the frontend and can be managed
    by the admin.
    """
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Event(models.Model):
    """
    Stores a single event entry related to :model:`auth.User`
    """
    class Difficulty(models.TextChoices):
        BEGINNER = "BEGINNER", "Beginner friendly"
        INTERMEDIATE = "INTERMEDIATE", "Intermediate"
        ADVANCED = "ADVANCED", "Advanced"

    title = models.CharField(max_length=200, unique=True)
    # allow blank so save() can populate the slug field
    slug = models.SlugField(unique=True, blank=True)
    organizer = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    # One event can have many categories, and a category can belong to 
    # many events
    category = models.ManyToManyField(
        Category, related_name="events"
        )
    difficulty = models.CharField(
        max_length=20, choices=Difficulty.choices, null=True
        )
    location = models.CharField(max_length=200)
    # Link and featured_image can be left blank
    link = models.URLField(blank=True, null=True)
    featured_image = CloudinaryField('image', default='placeholder', blank=True, null=True)
    cancelled = models.BooleanField(default=False)
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="events"
        )
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ["date", "start_time"]

    def __str__(self):
        return f"{self.title} | Organized by {self.organizer}"

    @property
    def is_past(self):
        """Returns True if the event's date and start_time are in the past."""
        # combine date + time
        event_dt = datetime.combine(self.date, self.start_time)
        # make it timezone-aware using Django's current timezone
        event_dt = timezone.make_aware(event_dt, timezone.get_current_timezone())
        return event_dt < timezone.localtime()
    
    # Automatically generate a slug for the model when you save it using a form
    def save(self, *args, **kwargs):
        if not self.slug:
            # Combine title and date in YYYY-MM-DD format
            date_str = self.date.strftime("%Y-%m-%d")
            self.slug = slugify(f"{self.title}-{date_str}")
        super().save(*args, **kwargs)

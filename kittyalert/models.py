"""Models for the 😻 Kitty Alert app"""

from django.contrib.auth import get_user_model
from django.db import models
from django_extensions.db.fields import AutoSlugField
from django_extensions.db.models import TimeStampedModel

User = get_user_model()


class Shelter(TimeStampedModel):
    """A shelter that has kitties up for adoption."""

    name = models.TextField(db_comment="The name of the shelter")
    slug = AutoSlugField(
        populate_from="name",
        unique=True,
        db_comment="The slug of the shelter, automatically generated from the name",
    )
    scrape_url = models.URLField(
        max_length=255, db_comment="The website URL of the shelter"
    )
    kitties = models.ManyToManyField(
        "Kitty",
        related_name="shelters",
    )


class Kitty(TimeStampedModel):
    """A kitty that is up for adoption."""

    class Meta:
        """Meta configuration for the Kitty model"""

        # Add unique constraint for description + image_url
        constraints = [
            models.UniqueConstraint(
                fields=["shelter", "description"],
                name="unique_kitty_by_description_and_image",
            )
        ]

    link = models.URLField(
        db_comment="The URL of the kitty's page on the shelter's website"
    )
    name = models.TextField(db_comment="The name of the kitty")
    age = models.TextField(db_comment="The age of the kitty in years")
    weight = models.TextField(db_comment="The weight of the kitty in pounds")
    gender = models.TextField(db_comment="The gender of the kitty")
    breed = models.TextField(db_comment="The breed of the kitty")
    color = models.TextField(db_comment="The color/pattern of the kitty")
    description = models.TextField(
        blank=True, null=True, db_comment="The description of the kitty"
    )
    shelter = models.ForeignKey(
        Shelter,
        on_delete=models.CASCADE,
        db_comment="The shelter where this kitty is available for adoption",
    )
    is_adopted = models.BooleanField(
        default=False, db_comment="Whether the kitty has been adopted"
    )
    image_urls = models.JSONField(
        blank=True, null=True, db_comment="The URLs of the kitty's images"
    )
    location = models.TextField(
        db_comment="The location of the kitty or whether they are bonded with another kitty"
    )


class Adopter(TimeStampedModel):
    """A user who is looking to adopt a kitty."""

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        db_comment="The Django user account associated with this adopter",
    )
    kitties = models.ManyToManyField(Kitty)
    email = models.EmailField(db_comment="The email address of the adopter")


class ScrapeRun(TimeStampedModel):
    """Tracks a single scraping operation for a shelter"""

    shelter = models.ForeignKey(
        Shelter,
        on_delete=models.CASCADE,
        related_name="scrape_runs",
        db_comment="The shelter that was scraped",
    )
    status = models.TextField(
        choices=[
            ("waiting", "Waiting"),
            ("running", "Running"),
            ("completed", "Completed"),
        ],
        default="waiting",
        db_comment="Current status of the scrape operation",
    )
    kitties_found = models.IntegerField(
        default=0, db_comment="Total number of kitties found during the scrape"
    )
    errors = models.JSONField(
        blank=True, null=True, db_comment="Errors encountered during the scrape"
    )
    raw_data = models.JSONField(
        blank=True,
        null=True,
        help_text="Raw scraped data for debugging",
        db_comment="Raw scraped data stored as JSON for debugging purposes",
    )

    class Meta:
        """Meta configuration for the ScrapeRun model"""

        indexes = [
            models.Index(fields=["shelter", "status"]),
        ]


class Subscription(TimeStampedModel):
    """A subscription to a shelter's kitty alerts"""

    adopter = models.ForeignKey(
        Adopter,
        on_delete=models.CASCADE,
        related_name="subscriptions",
        db_comment="The adopter that is subscribed to this shelter's kitties",
    )
    shelter = models.ForeignKey(
        Shelter,
        on_delete=models.CASCADE,
        related_name="subscriptions",
        db_comment="The shelter that is subscribed to",
    )


class Notification(TimeStampedModel):
    """A notification for a subscription"""

    class Meta:
        """Meta configuration for the Notification model"""

        indexes = [
            models.Index(fields=["subscription", "-created"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["subscription", "scrape_run"],
                name="unique_notification_by_subscription_and_scrape_run",
            )
        ]

    subscription = models.ForeignKey(
        Subscription,
        on_delete=models.CASCADE,
        related_name="notifications",
        db_comment="The subscription that was notified",
    )
    scrape_run = models.ForeignKey(
        ScrapeRun,
        on_delete=models.CASCADE,
        related_name="notifications",
        db_comment="The scrape run that was used to send the notification",
    )
    email_sent_at = models.DateTimeField(
        blank=True,
        null=True,
        db_comment="The time the email was sent",
    )
    errors = models.JSONField(
        blank=True,
        null=True,
        db_comment="Errors encountered during the notification",
    )

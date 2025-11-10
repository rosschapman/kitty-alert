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
        db_comment="Kitties that are available for adoption at this shelter",
    )


class Kitty(TimeStampedModel):
    """A kitty that is up for adoption."""

    name = models.TextField(db_comment="The name of the kitty")
    age = models.IntegerField(db_comment="The age of the kitty in years")
    weight = models.IntegerField(db_comment="The weight of the kitty in pounds")
    gender = models.TextField(db_comment="The gender of the kitty")
    breed = models.TextField(db_comment="The breed of the kitty")
    color = models.TextField(db_comment="The color/pattern of the kitty")
    image_url = models.URLField(
        db_comment="URL of the kitty's image on the SFPCA website",
    )
    shelter = models.ForeignKey(
        Shelter,
        on_delete=models.CASCADE,
        db_comment="The shelter where this kitty is available for adoption",
    )
    is_adopted = models.BooleanField(
        default=False, db_comment="Whether the kitty has been adopted"
    )


class Adopter(TimeStampedModel):
    """A user who is looking to adopt a kitty."""

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        db_comment="The Django user account associated with this adopter",
    )
    kitties = models.ManyToManyField(
        Kitty, db_comment="Kitties that this adopter has saved/alerts for"
    )


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
            ("success", "Successful"),
            ("failed", "Failed"),
        ],
        default="waiting",
        db_comment="Current status of the scrape operation",
    )
    kitties_found = models.IntegerField(
        default=0, db_comment="Total number of kitties found during the scrape"
    )
    kitties_new = models.IntegerField(
        default=0, db_comment="Number of new kitties discovered in this scrape"
    )
    error_message = models.TextField(
        blank=True, null=True, db_comment="Error message if the scrape failed"
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

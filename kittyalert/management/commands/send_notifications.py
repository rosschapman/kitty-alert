from django.core.management.base import BaseCommand
from django.utils import timezone

from kittyalert.email import format_kitty_notification, send_email_notification
from kittyalert.models import Notification, ScrapeRun, Subscription


class Command(BaseCommand):
    help = "Send email notifications for new kitties to all subscribers"

    def handle(self, *args, **options):
        """Send email notifications for new kitties to all subscribers of the
        last scrape run"""

        sent_count = 0

        # Get the latest and previous scrape runs
        scrape_runs = ScrapeRun.objects.order_by("-created")[:2]

        if len(scrape_runs) < 2:
            self.stdout.write(
                self.style.WARNING("Need at least 2 scrape runs to compare. Skipping.")
            )
            return

        latest_scrape_run = scrape_runs[0]
        latest_scrape_run_data = latest_scrape_run.raw_data or []

        subscriptions = Subscription.objects.select_related("adopter", "adopter__user")

        if not subscriptions.exists():
            self.stdout.write(
                self.style.WARNING(f"No subscriptions found. No notifications sent.")
            )
            return

        for subscription in subscriptions:
            last_notification = (
                Notification.objects.filter(
                    subscription=subscription,
                )
                .order_by("-created")
                .first()
            )

            previous_scrape_run = (
                last_notification.scrape_run
                if last_notification
                else ScrapeRun.objects.filter(shelter=subscription.shelter).order_by(
                    "-created"
                )[1]
            )

            previous_scrape_run_data = previous_scrape_run.raw_data or []
            previous_scrape_run_descriptions = {
                kitty_data["description"] for kitty_data in previous_scrape_run_data
            }

            new_kitties = [
                kitty_data
                for kitty_data in latest_scrape_run_data
                if kitty_data.get("description", "")
                not in previous_scrape_run_descriptions
            ]

            if not new_kitties:
                self.stdout.write(
                    self.style.SUCCESS("No new kitties found. No notifications sent.")
                )
                return

            subject, message = format_kitty_notification(
                new_kitties, subscription.shelter.name, subscription.shelter.scrape_url
            )

            notification = Notification.objects.create(
                subscription=subscription,
                scrape_run=latest_scrape_run,
            )
            adopter = subscription.adopter
            user_email = adopter.user.email
            if not user_email:
                self.stdout.write(
                    self.style.WARNING(
                        f"Skipping {adopter.user.username} - no email address"
                    )
                )
                continue

            success = send_email_notification(user_email, subject, message)
            notification.email_sent_at = timezone.now()
            notification.save()
            if success:
                sent_count += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Sent notification to {adopter.user.username} at {user_email}"
                    )
                )
            else:
                notification.errors = [f"Failed to send email to {user_email}"]
                notification.save()
                self.stdout.write(
                    self.style.ERROR(
                        f"Failed to send notification to {adopter.user.username} at {user_email}"
                    )
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"\nNotifications sent: {sent_count} | New kitties: {len(new_kitties)}"
            )
        )

from django.core.management.base import BaseCommand

from kittyalert.email import format_kitty_notification, send_email_notification
from kittyalert.models import ScrapeRun, Subscription


class Command(BaseCommand):
    help = "Send email notifications for new kitties to all subscribers"

    def handle(self, *args, **options):
        """Send email notifications for new kitties to all subscribers of the last scrape run"""

        # Get the latest and previous scrape runs
        scrape_runs = ScrapeRun.objects.order_by("-created")[:2]
        if len(scrape_runs) < 2:
            self.stdout.write(
                self.style.WARNING("Need at least 2 scrape runs to compare. Skipping.")
            )
            return

        latest_scrape_run = scrape_runs[0]
        previous_scrape_run = scrape_runs[1]

        # Find new kitties by comparing descriptions
        previous_scrape_run_descriptions = {
            kitty_data.get("description", "")
            for kitty_data in previous_scrape_run.raw_data or []
        }

        new_kitties = [
            kitty_data
            for kitty_data in latest_scrape_run.raw_data or []
            if kitty_data.get("description", "") not in previous_scrape_run_descriptions
        ]

        if not new_kitties:
            self.stdout.write(
                self.style.SUCCESS("No new kitties found. No notifications sent.")
            )
            return

        # Get all subscriptions for this shelter
        shelter = latest_scrape_run.shelter
        subscriptions = Subscription.objects.filter(shelter=shelter).select_related(
            "adopter", "adopter__user"
        )

        if not subscriptions.exists():
            self.stdout.write(
                self.style.WARNING(
                    f"No subscriptions found for {shelter.name}. No notifications sent."
                )
            )
            return

        subject, message = format_kitty_notification(
            new_kitties, shelter.name, shelter.scrape_url
        )

        sent_count = 0

        for subscription in subscriptions:
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
            if success:
                sent_count += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Sent notification to {adopter.user.username} at {user_email}"
                    )
                )
            else:
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

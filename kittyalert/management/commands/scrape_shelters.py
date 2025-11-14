from django.core.management.base import BaseCommand

from kittyalert.models import ScrapeRun, Shelter
from kittyalert.scraper import scrape_shelter


class Command(BaseCommand):
    help = "Scrape all shelters for new kitties"

    def handle(self, *args, **options):
        shelters = Shelter.objects.all()
        scrape_runs = []

        for shelter in shelters:
            self.stdout.write(f"Fetching kitties from {shelter.name}...")
            scrape_run = ScrapeRun.objects.create(status="running", shelter=shelter)

            kitties, errors = scrape_shelter(shelter)

            if errors:
                self.stdout.write(
                    self.style.WARNING(f"Errors for {shelter.name}: {errors}")
                )
            self.stdout.write(
                self.style.SUCCESS(
                    f"Successfully scraped {shelter.name}: {len(kitties)} kitties found"
                )
            )
            scrape_run.kitties_found = len(kitties)
            scrape_run.errors = errors
            scrape_run.raw_data = kitties
            scrape_run.status = "completed"
            scrape_run.save()
            scrape_runs.append(scrape_run.id)

        self.stdout.write(
            self.style.SUCCESS(
                f"Completed {len(scrape_runs)} scrape run(s) with ids: {', '.join(scrape_runs)}"
            )
        )

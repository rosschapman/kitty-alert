"""Views for the 😻 Kitty Alert app"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .models import Adopter, Kitty, ScrapeRun, Shelter
from .scraper import scrape_shelter


def home(request):
    """View to display the home page which redirects to the adopter dashboard if the user is authenticated"""

    if request.user.is_authenticated:
        return redirect("adopter_detail", adopter_id=request.user.adopter.id)
    else:
        return redirect("login")


@login_required
def adopter_detail(request, adopter_id):
    """View to display the dashboard for a single adopter"""

    adopter = Adopter.objects.get(id=adopter_id)
    return render(request, "adopters/detail.html", {"adopter": adopter})


@login_required
def kitty_list(request):
    """View to display the list of kitties"""
    adopter = Adopter.objects.get(user=request.user)
    scrape_run = ScrapeRun.objects.create(
        shelter=Shelter.objects.get(slug="sf-spca"),
    )

    # Separating creation from run for now until we add a trigger
    scrape_run.status = "running"
    scrape_run.save()
    try:
        kitties = scrape_shelter(Shelter.objects.get(slug="sf-spca"))
        scrape_run.status = "success"
        scrape_run.save()
    except Exception as e:
        scrap_run.status = "failed"
        scrap_run.error_message = str(e)
        scrap_run.save()
        return render(request, "kitties/list.html", {"error": str(e)})
    return render(
        request, "kitties/list.html", {"kitties": kitties, "adopter": adopter}
    )


@login_required
def kitty_save(request, kitty_id, adopter_id):
    """View to save a kitty"""
    adopter = Adopter.objects.get(id=adopter_id)
    kitty = Kitty.objects.get(id=kitty_id)
    adopter.kitties.add(kitty)
    messages.success(request, f"Saved {kitty.name} to your list!")
    return redirect("kitty_list")


@login_required
def kitty_unsave(request, kitty_id, adopter_id):
    """View to unsave a kitty"""
    adopter = Adopter.objects.get(id=adopter_id)
    kitty = Kitty.objects.get(id=kitty_id)
    adopter.kitties.remove(kitty)
    messages.success(request, f"Removed {kitty.name} from your list.")
    return redirect("kitty_list")

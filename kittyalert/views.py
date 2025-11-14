"""Views for the 😻 Kitty Alert app"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.db.models import Exists, OuterRef
from django.shortcuts import redirect, render

from .models import Adopter, Kitty, ScrapeRun, Shelter, Subscription


def home(request):
    """View to display the home page which redirects to the adopter dashboard if the user is authenticated"""

    if request.user.is_authenticated:
        return redirect("adopter_dashboard", adopter_id=request.user.adopter.id)
    else:
        return redirect("login")


@login_required
def adopter_dashboard(request, adopter_id):
    """View to display the dashboard for a single adopter"""

    # Use select_related to fetch the user in the same query, avoiding N+1 queries
    # Prefetch kitties to avoid additional queries when iterating in template
    adopter = (
        Adopter.objects.select_related("user")
        .prefetch_related("kitties")
        .get(id=adopter_id)
    )
    # Annotate shelters with subscription status in a single efficient query
    shelters = Shelter.objects.annotate(
        is_subscribed=Exists(
            Subscription.objects.filter(adopter=adopter, shelter=OuterRef("pk"))
        )
    )
    return render(
        request,
        "adopters/dashboard.html",
        {
            "adopter": adopter,
            "shelters": shelters,
        },
    )


@login_required
def shelter_kitty_list(request, shelter_id):
    """View to display the list of kitties

    Cached for 24 hours to avoid repeated scrapes.
    """
    adopter = Adopter.objects.get(user=request.user)
    adopter_kitties = adopter.kitties.all()
    latest_scrape_run = ScrapeRun.objects.order_by("-created").first()

    cache_key = (
        f"kitty_list_{latest_scrape_run.created.timestamp()}"
        if latest_scrape_run
        else None
    )
    cache_hit = cache.get(cache_key)

    if cache_hit:
        kitties = cache_hit["kitties"]
        errors = cache_hit["errors"]
    else:
        kitties = latest_scrape_run.raw_data
        errors = latest_scrape_run.errors
        cache.set(cache_key, {"kitties": kitties, "errors": errors})

    # No need to create image_urls_json anymore since we're using multiple inputs

    return render(
        request,
        "shelters/list.html",
        {
            "kitties": kitties,
            "adopter": adopter,
            "adopter_kitties": adopter_kitties,
            "errors": errors,
            "shelter": Shelter.objects.get(id=shelter_id),
        },
    )


@login_required
def kitty_save(request, adopter_id):
    """View to save a kitty"""
    adopter = Adopter.objects.get(id=adopter_id)

    kitty, created = Kitty.objects.get_or_create(
        shelter=Shelter.objects.get(slug="sf-spca"),
        description=request.POST["description"],
        defaults={
            "name": request.POST["name"],
            "image_urls": request.POST.getlist("image_urls"),
            "weight": request.POST["weight"],
            "gender": request.POST["gender"],
            "breed": request.POST["breed"],
            "link": request.POST["link"],
        },
    )

    if adopter.kitties.filter(id=kitty.id).exists():
        messages.warning(request, f"{kitty.name} is already in your list!")

        return redirect("adopter_dashboard", adopter_id=adopter_id)

    adopter.kitties.add(kitty)
    messages.success(request, f"Saved {kitty.name} to your list!")
    return redirect("adopter_dashboard", adopter_id=adopter_id)


@login_required
def kitty_unsave(request, adopter_id, kitty_id):
    """View to unsave a kitty"""
    adopter = Adopter.objects.get(id=adopter_id)
    kitty = Kitty.objects.get(id=kitty_id)
    adopter.kitties.remove(kitty)
    messages.success(request, f"Removed {kitty.name} from your list.")
    return redirect("adopter_dashboard", adopter_id=adopter_id)


@login_required
def subscribe_to_shelter(request, adopter_id, shelter_id):
    """View to subscribe to a shelter"""
    adopter = Adopter.objects.get(id=adopter_id)
    shelter = Shelter.objects.get(id=shelter_id)
    Subscription.objects.create(adopter=adopter, shelter=shelter)
    messages.success(request, f"Subscribed to {shelter.name}.")
    return redirect("adopter_dashboard", adopter_id=adopter_id)


@login_required
def unsubscribe_from_shelter(request, adopter_id, shelter_id):
    """View to unsubscribe from a shelter"""
    adopter = Adopter.objects.get(id=adopter_id)
    shelter = Shelter.objects.get(id=shelter_id)
    Subscription.objects.filter(adopter=adopter, shelter=shelter).delete()
    messages.success(request, f"Unsubscribed from {shelter.name}.")
    return redirect("adopter_dashboard", adopter_id=adopter_id)

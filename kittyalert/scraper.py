"""Scraper for the 😻 Kitty Alert app"""

import logging
from typing import Any

from playwright.sync_api import sync_playwright

logger = logging.getLogger(__name__)


def scrape_shelter(shelter) -> tuple[list[dict[str, Any]], list]:
    """Scrape the shelter website for kitty data.

    Args:
        shelter: A Shelter model instance

    Returns:
        Tuple of (list of dictionaries containing kitty data, list of errors)
    """
    kitties_data = []
    errors = []

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            page.goto(shelter.scrape_url, wait_until="domcontentloaded")

            try:
                page.wait_for_selector(".adoption__item", timeout=5000)
            except TimeoutError:
                logger.warning(
                    "Timeout waiting for kitty cards on %s", shelter.scrape_url
                )
                return [], []

            kitty_cards = page.query_selector_all(".adoption__item")
            card_links = []

            for card in kitty_cards:
                name_element = card.query_selector(".adoption__item--name a")
                name_text = name_element.inner_text().strip()
                card_link = name_element.get_attribute("href")
                location_text = (
                    page.query_selector(".adoption__item--location")
                    .inner_text()
                    .strip()
                )
                card_links.append(
                    {"name": name_text, "link": card_link, "location": location_text}
                )

            for card_info in card_links:
                try:
                    name_text = card_info["name"]
                    card_link = card_info["link"]

                    page.goto(card_link, wait_until="domcontentloaded")

                    try:
                        page.wait_for_selector(
                            ".elementor-widget-theme-post-content .elementor-widget-container",
                            timeout=5000,
                        )
                    except TimeoutError:
                        logger.warning(
                            "Timeout waiting for card content on %s", card_link
                        )

                    description_element = page.query_selector(
                        ".elementor-widget-theme-post-content .elementor-widget-container"
                    )
                    card_text = (
                        description_element.inner_html()
                        if description_element
                        else "Unknown"
                    )

                    facts_element = page.query_selector(
                        ".elementor-widget-adoption-facts .elementor-widget-container"
                    )

                    age_text = (
                        facts_element.query_selector_all("p")[0]
                        .inner_text()
                        .strip()
                        .split("Age:")[-1]
                    )

                    weight_text = (
                        facts_element.query_selector_all("p")[1]
                        .inner_text()
                        .strip()
                        .split("Weight:")[-1]
                    )

                    gender_text = (
                        facts_element.query_selector_all("p")[2]
                        .inner_text()
                        .strip()
                        .split("Gender:")[-1]
                    )

                    breed_text = (
                        facts_element.query_selector_all("p")[3]
                        .inner_text()
                        .strip()
                        .split("Breed:")[-1]
                    )

                    image_urls = [
                        img.get_attribute("src")
                        for img in page.query_selector_all(".swiper-slide-image")
                    ]

                    kitty_data = {
                        "link": card_link,
                        "name": name_text,
                        "age": age_text,
                        "weight": weight_text,
                        "gender": gender_text,
                        "breed": breed_text,
                        "color": "TODO",  # TODO: Extract color from image
                        "description": card_text,
                        "image_urls": image_urls,
                        "location": location_text,
                    }
                    kitties_data.append(kitty_data)

                except Exception as e:
                    logger.error("Error extracting kitty data: %s", e)
                    errors.append(e)
                    continue

            browser.close()

    except Exception as e:
        errors = [str(e)]
        return [], errors

    return kitties_data, errors

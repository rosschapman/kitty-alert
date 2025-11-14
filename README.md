# 😻 Kitty Alert

## Requirements & Scope

### User Stories
- As an adopter, I want an alert anytime a new kitty is up for adoption from the SFPCA
- As an adopter, I want the alert to contain the name, age, weight, gender,
  breed, and color of the kitty, and include a link to to the SFPCA adoption page
- ✅ As an adopter, I want the option to save the kitty
- ✅As an adopter, I want the ability view saved kitties
- ✅ As an adopter, I want the ability to share all my saved kitties

### Implementation

- Ensure a scrape exists by running on startup
- ✅ Cache kitties list page per run

#### Architecture

- No image storage

### Entities
- Adopter
- Shelter
- Kitty
- ScrapeRun

### Resources
- https://www.sfspca.org/adoptions/cats/

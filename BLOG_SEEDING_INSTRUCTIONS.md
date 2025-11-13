# Adding Insight Seed Posts per Service

This guide shows how to load or update blog (“Insight”) entries for each Hammer service using the existing seeding scripts.

## 1. Activate the project environment

```bash
cd myProject
.\myenv\Scripts\activate  # Windows PowerShell
# or
source myenv/bin/activate  # macOS / Linux
```

## 2. Seed landscape posts

The script at `create_insights.py` currently seeds landscape-focused content. Run:

```bash
python create_insights.py --service landscape-design-build
```

- Imports the Hammer app and ensures `django.setup()` is called.
- Loops through the `POSTS` list; for each entry it runs `Insight.objects.get_or_create(...)` so existing titles are updated, new ones are added.
- **No deletions happen** unless you pass `--reset`.

To replace landscape posts entirely:

```bash
python create_insights.py --service landscape-design-build --reset
```

`--reset` deletes all insights tied to that service before reseeding.

## 3. Seed other services

Follow the same pattern for additional services—each seed script expects the service slug.

### Interior Design

```bash
python create_insights.py --service interior-design-build
```

> Make sure a script or POSTS list exists for interior. If you build a dedicated script (e.g. `create_insights_interior.py`), follow the same structure: import Django, define POSTS, call `seed_insights()` with the desired slug.

### Facility Management / Aftercare

```bash
python create_insights.py --service facility-management
```

### Joinery

```bash
python create_insights.py --service joinery
```

### Marble / Stone

```bash
python create_insights.py --service marble
```

### Generic “Services” landing content

```bash
python create_insights.py --service services
```

> The slug must match the `Service.slug` field in the database. You can confirm by opening the Django admin or querying `Service.objects.values_list("slug", flat=True)`.

## 4. Creating a new seed file

If a service does not have a pre-built seed script:

1. Copy `create_insights.py` to a descriptive name, e.g. `create_insights_interior.py`.
2. Update the `POSTS` array with the titles, tags, excerpts, bodies, and images for that service.
3. Adjust the default slug in `seed_insights(...)` if desired.
4. Run `python create_insights_interior.py --service interior-design-build`.

## 5. Verifying results

- Visit `/dashboard/insights/` to confirm the new posts appear.
- Each run logs how many entries were created vs. updated:

```
Seeded/updated 1 insights for 'landscape-design-build'. Total now: 5.
```

## Quick Reference

| Service | Example Slug | Command |
| --- | --- | --- |
| Landscape Design & Build | `landscape-design-build` | `python create_insights.py --service landscape-design-build` |
| Interior Design & Build | `interior-design-build` | `python create_insights.py --service interior-design-build` |
| Facility Management | `facility-management` | `python create_insights.py --service facility-management` |
| Joinery | `joinery` | `python create_insights.py --service joinery` |
| Marble / Stone | `marble` | `python create_insights.py --service marble` |
| Services Overview | `services` | `python create_insights.py --service services` |

Remember: use `--reset` only when you intentionally want to wipe existing posts for a service before seeding fresh content.


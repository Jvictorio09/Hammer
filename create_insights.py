# create_insights.py
import os
import django
import argparse
from django.utils.text import slugify

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myProject.settings")
django.setup()

from django.utils import timezone
from myApp.models import Service, Insight

def unique_slug(base, exists):
    """
    Ensure unique slug by suffixing -2, -3, ...
    `exists` should be a callable that returns True if slug exists.
    """
    slug = slugify(base)[:60] or "post"
    if not exists(slug):
        return slug
    i = 2
    while True:
        trial = f"{slug}-{i}"
        if not exists(trial):
            return trial
        i += 1

def seed_insights(service_slug: str, reset: bool = False):
    try:
        svc = Service.objects.get(slug=service_slug)
    except Service.DoesNotExist:
        print(f"✗ Service with slug '{service_slug}' not found. Create it first.")
        return 1

    if reset:
        deleted = Insight.objects.filter(service=svc).delete()[0]
        print(f"• Deleted {deleted} existing insights for '{service_slug}'")

    posts = [
        dict(
            title="How to fix budgets before drawings",
            tag="Pre-Con",
            read_minutes=4,
            excerpt="Pre-con that prevents “surprise” costs.",
            cover_image_url="https://picsum.photos/600/400?random=561",
        ),
        dict(
            title="Joinery that lasts: a materials guide",
            tag="Joinery",
            read_minutes=6,
            excerpt="What to specify—and what to avoid—in Dubai.",
            cover_image_url="https://picsum.photos/600/400?random=562",
        ),
        dict(
            title="Landscapes that reduce water use",
            tag="Landscape",
            read_minutes=3,
            excerpt="Native planting, smart irrigation, real savings.",
            cover_image_url="https://picsum.photos/600/400?random=563",
        ),
        dict(
            title="The post-handover plan you need",
            tag="Aftercare",
            read_minutes=5,
            excerpt="FM that protects asset value from day one.",
            cover_image_url="https://picsum.photos/600/400?random=564",
        ),
    ]

    created = 0
    for p in posts:
        # make a unique slug per title within all insights
        def exists(slug): return Insight.objects.filter(slug=slug).exists()
        slug = unique_slug(p["title"], exists)

        obj, was_created = Insight.objects.get_or_create(
            service=svc,
            title=p["title"],
            defaults=dict(
                slug=slug,
                tag=p["tag"],
                read_minutes=p["read_minutes"],
                excerpt=p["excerpt"],
                cover_image_url=p["cover_image_url"],
                body=(
                    "<p>We’ll soon publish the full article. In the meantime, talk to our team "
                    "for a tailored walkthrough of budgets, sequencing and risk controls for your scope.</p>"
                ),
                published=True,
                published_at=timezone.now(),
            ),
        )
        if was_created:
            created += 1

    total = Insight.objects.filter(service=svc).count()
    print(f"✓ Seeded {created} new insights for '{service_slug}'. Total now: {total}.")
    return 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--service", default="landscape", help="Service slug (default: landscape)")
    parser.add_argument("--reset", action="store_true", help="Delete existing insights for this service first")
    args = parser.parse_args()
    raise SystemExit(seed_insights(args.service, args.reset))

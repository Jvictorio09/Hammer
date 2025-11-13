from __future__ import annotations

import os
import sys
import typing as t
import uuid
import re

import django
from django.utils import timezone
from django.utils.text import slugify

# --- Django setup (run standalone) ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myProject.settings")
django.setup()

from myApp.models import Service, Insight  # noqa: E402


def unique_slug(base: str) -> str:
    """Make a globally-unique slug for Insight by suffixing -2, -3, ..."""
    seed = (slugify(base)[:60] or "post").strip("-")
    if not Insight.objects.filter(slug=seed).exists():
        return seed
    i = 2
    while True:
        trial = f"{seed}-{i}"
        if not Insight.objects.filter(slug=trial).exists():
            return trial
        i += 1


def html_to_editorjs_blocks(html_content: str) -> dict:
    """Convert minimal HTML to Editor.js blocks."""
    if not html_content or not html_content.strip():
        return {"time": int(timezone.now().timestamp() * 1000), "blocks": [], "version": "2.28.2"}

    blocks = []
    for raw in html_content.split("\n"):
        line = raw.strip()
        if not line:
            continue

        def strip_tags(s: str) -> str:
            return re.sub(r"<[^>]+>", "", s).strip()

        if line.startswith("<h1>"):
            txt = strip_tags(line)
            if txt: blocks.append({"id": str(uuid.uuid4()), "type": "header", "data": {"text": txt, "level": 1}})
        elif line.startswith("<h2>"):
            txt = strip_tags(line)
            if txt: blocks.append({"id": str(uuid.uuid4()), "type": "header", "data": {"text": txt, "level": 2}})
        elif line.startswith("<blockquote>"):
            txt = strip_tags(line)
            if txt: blocks.append({"id": str(uuid.uuid4()), "type": "quote", "data": {"text": txt, "caption": ""}})
        elif line.startswith("<ul>"):
            continue
        elif line.startswith("<li>"):
            txt = strip_tags(line)
            if txt: blocks.append({"id": str(uuid.uuid4()), "type": "list", "data": {"style": "unordered", "items": [txt]}})
        elif line.startswith("<p>"):
            txt = strip_tags(line)
            if txt: blocks.append({"id": str(uuid.uuid4()), "type": "paragraph", "data": {"text": txt}})
        elif line and not line.startswith("<"):
            blocks.append({"id": str(uuid.uuid4()), "type": "paragraph", "data": {"text": line}})

    return {"time": int(timezone.now().timestamp() * 1000), "blocks": blocks, "version": "2.28.2"}


# ---- Hammer Interiors Insight: Biophilic Design (2025) ----
POSTS: t.List[dict] = [
    {
        "title": "🌿 Bring Nature Indoors: Biophilic Design Ideas for Dubai Homes in 2025",
        "tag": "Nature",
        "read_minutes": 7,
        "excerpt": "How to transform your villa into a lush oasis with living walls, indoor gardens, and natural materials — a guide to biophilic design for Dubai’s climate.",
        "cover_image_url": (
            "https://images.unsplash.com/photo-1501785888041-af3ef285b470?"
            "w=1600&q=80&auto=format&fit=crop"
        ),
        "body": """
<h1>🌿 Bring Nature Indoors: Biophilic Design Ideas for Dubai Homes in 2025</h1>
<p><em>Meta Description:</em> Discover how <strong>biophilic design in Dubai</strong> connects you to nature through living walls, indoor gardens, natural materials, and water features. Learn how to select the right plants and materials for the desert climate and elevate your home’s well-being with Hammer’s interior experts.</p>

<p>In a city that thrives on skyscrapers and desert vistas, it’s easy to forget how soothing nature can be. <strong>Biophilic design</strong> brings that connection back by weaving greenery and natural elements into our living spaces. According to design experts, this approach promotes harmony with nature and turns interiors into an oasis. More homeowners in Dubai are embracing this trend to soften sleek architecture and create healthier, more serene homes.</p>

<h2>Why Biophilic Design Matters</h2>
<p>Modern life often keeps us indoors under artificial light, which can stress our bodies and minds. Studies show that spaces rich in natural elements — plants, light, water, and organic materials — reduce stress, boost productivity, and inspire creativity. Biophilic design isn’t just about aesthetics; it’s about improving well-being by inviting nature into your home. In Dubai’s hot climate, thoughtfully integrating greenery can also help regulate indoor temperatures and air quality.</p>

<h2>Living Walls: Green Art with a Purpose</h2>
<p>Living walls (also called vertical gardens) are hydroponic or soil-based plant systems that turn plain walls into vibrant natural artworks. They provide natural insulation and air filtration, removing indoor toxins and reducing the heat island effect.</p>
<p>In Dubai villas, living walls can line entryways, frame staircases, or anchor a courtyard. Choose drought-tolerant plants like philodendron, pothos, and succulents, and install automatic drip irrigation to keep them thriving with minimal water use.</p>

<h2>Indoor Gardens &amp; Hanging Plants</h2>
<p>Beyond living walls, create pockets of green by installing hanging planters, window boxes, and potted trees. Green partitions and hanging plants improve indoor air quality and introduce a calming environment.</p>
<p>Position trailing plants near windows or double-height ceilings for dramatic effect, and use leafy species such as palms, fiddle-leaf figs, or dracaenas that adapt well to Dubai’s climate.</p>

<h2>Natural Materials &amp; Textures</h2>
<p>Integrate biophilic design in finishes and furniture by choosing natural materials like wood, stone, and bamboo. These materials ground interiors and evoke an organic warmth that complements greenery.</p>
<p>For floors and countertops, opt for engineered wood or microcement that lasts in Dubai’s climate. Pair these with woven textiles and tactile surfaces to engage the senses and create a sense of refuge.</p>

<h2>Water Features &amp; Acoustic Calm</h2>
<p>Water is a powerful biophilic element. Incorporate indoor fountains, reflective pools, or tabletop waterfalls to introduce soothing sound and humidity. Even small features can mimic the calming effect of a stream, enhancing the overall sensory experience and balancing the desert air.</p>

<h2>Lighting &amp; Natural Cycles</h2>
<p>Biophilic design thrives with natural light. Use large windows, skylights, light wells, and translucent partitions to maximise daylight. Complement this with tunable LED lighting that shifts color temperature to match the natural day–night cycle, supporting circadian rhythms and wellness.</p>

<h2>Tailoring Biophilic Design to Dubai’s Climate</h2>
<p>While lush greenery might seem counterintuitive in a desert city, careful species selection and smart irrigation make it sustainable. Prioritise drought-tolerant native and regional plants such as the ghaf tree, bougainvillea, and desert rose, which thrive on minimal water.</p>
<p>Use hydrozoning techniques — grouping plants with similar water needs — and install efficient drip systems that deliver water directly to roots to reduce waste.</p>

<h2>Ready to Bring Nature Home?</h2>
<p>Biophilic design isn’t a trend; it’s a shift toward healthier, more human-centric spaces. By choosing the right plants, materials, and design strategies, you can transform your villa into a sanctuary that nurtures both body and soul.</p>
<p>If you’re ready to explore how biophilic interiors can enhance your Dubai home, our interior team is here to help. From concept to installation, we’ll tailor every element to harmonise with your architecture and lifestyle.</p>
<p><strong>Contact Hammer Interiors</strong></p>
""",
    },
]


def seed_insights(service_slug: str = "interior-design-build", reset: bool = False) -> None:
    try:
        svc = Service.objects.get(slug=service_slug)
    except Service.DoesNotExist:
        print(f"Service with slug '{service_slug}' not found. Create it first.")
        return

    if reset:
        deleted = Insight.objects.filter(service=svc).delete()[0]
        print(f"Deleted {deleted} existing insights for '{service_slug}'")

    created = 0
    for p in POSTS:
        slug = unique_slug(p["title"])
        blocks_data = html_to_editorjs_blocks(p["body"])

        obj, was_created = Insight.objects.get_or_create(
            service=svc,
            title=p["title"],
            defaults={
                "slug": slug,
                "tag": p["tag"],
                "read_minutes": p["read_minutes"],
                "excerpt": p["excerpt"],
                "cover_image_url": p["cover_image_url"],
                "body": p["body"].strip(),
                "blocks": blocks_data,
                "published": True,
                "published_at": timezone.now(),
            },
        )
        if was_created:
            created += 1
        else:
            obj.tag = p["tag"]
            obj.read_minutes = p["read_minutes"]
            obj.excerpt = p["excerpt"]
            obj.cover_image_url = p["cover_image_url"]
            obj.body = p["body"].strip()
            obj.blocks = blocks_data
            obj.published = True
            if not obj.published_at:
                obj.published_at = timezone.now()
            obj.save()

    total = Insight.objects.filter(service=svc).count()
    print(f"Seeded/updated {created} insights for '{service_slug}'. Total now: {total}.")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Seed Hammer Interiors insights for a service")
    parser.add_argument("--service", default="interior-design-build", help="Service slug")
    parser.add_argument("--reset", action="store_true", help="Delete existing insights before seeding")
    args = parser.parse_args()

    seed_insights(args.service, args.reset)

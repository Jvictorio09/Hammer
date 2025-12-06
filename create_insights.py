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
        return {
            "time": int(timezone.now().timestamp() * 1000),
            "blocks": [],
            "version": "2.28.2",
        }

    blocks = []
    for raw in html_content.split("\n"):
        line = raw.strip()
        if not line:
            continue

        def strip_tags(s: str) -> str:
            return re.sub(r"<[^>]+>", "", s).strip()

        if line.startswith("<h1>"):
            txt = strip_tags(line)
            if txt:
                blocks.append(
                    {
                        "id": str(uuid.uuid4()),
                        "type": "header",
                        "data": {"text": txt, "level": 1},
                    }
                )
        elif line.startswith("<h2>"):
            txt = strip_tags(line)
            if txt:
                blocks.append(
                    {
                        "id": str(uuid.uuid4()),
                        "type": "header",
                        "data": {"text": txt, "level": 2},
                    }
                )
        elif line.startswith("<blockquote>"):
            txt = strip_tags(line)
            if txt:
                blocks.append(
                    {
                        "id": str(uuid.uuid4()),
                        "type": "quote",
                        "data": {"text": txt, "caption": ""},
                    }
                )
        elif line.startswith("<ul>"):
            continue
        elif line.startswith("<li>"):
            txt = strip_tags(line)
            if txt:
                blocks.append(
                    {
                        "id": str(uuid.uuid4()),
                        "type": "list",
                        "data": {"style": "unordered", "items": [txt]},
                    }
                )
        elif line.startswith("<p>"):
            txt = strip_tags(line)
            if txt:
                blocks.append(
                    {
                        "id": str(uuid.uuid4()),
                        "type": "paragraph",
                        "data": {"text": txt},
                    }
                )
        elif line and not line.startswith("<"):
            blocks.append(
                {
                    "id": str(uuid.uuid4()),
                    "type": "paragraph",
                    "data": {"text": line},
                }
            )

    return {
        "time": int(timezone.now().timestamp() * 1000),
        "blocks": blocks,
        "version": "2.28.2",
    }


# ---- Hammer Services Insight: Best Landscape Contractor in Dubai (2025) ----
POSTS: t.List[dict] = [
    {
        "title": "What Makes a Landscape Contractor \"The Best\" in Dubai — And Why Hammer Services Leads the List (2025 Guide)",
        "tag": "Outdoor Living",  # Primary tag (max 40 chars) - using main category
        "read_minutes": 8,
        "tags": [
            "100 Projects",
            "aluminium pergola",
            "aluminum pergola",
            "ANSA7K SERVICES",
            "Artificial Grass",
            "backyard",
            "Backyard Design",
            "backyard landscape design company in dubai",
            "backyard landscape designs",
            "backyard landscaping",
        ],
        "categories": [
            "Events",
            "Firepits",
            "Maintenance",
            "Outdoor Kitchen",
            "Outdoor Lighting",
            "Outdoor Living",
            "Pavers and Slabs",
            "Pergolas",
            "Planter box",
            "Seating Area",
        ],
        "excerpt": (
            "In Dubai, the best landscape contractors don’t just decorate — they engineer outdoor "
            "living environments for extreme heat, drainage, and luxury standards. This 2025 guide "
            "explains what truly sets top firms apart and why Hammer Services leads the list."
        ),
        "cover_image_url": (
            # Swap this for a Hammer / Cloudinary outdoor living hero when ready
            "https://images.unsplash.com/photo-1500534314211-0a24cd03f2c0?"
            "w=1600&q=80&auto=format&fit=crop"
        ),
        "body": """
<h1>What Makes a Landscape Contractor “The Best” in Dubai — And Why Hammer Services Leads the List (2025 Guide)</h1>

<p><strong>Hammer Services Dubai</strong><br>
<em>Category: Landscaping &amp; Outdoor Living</em></p>

<p>When people imagine Dubai landscapes, they think of lush gardens, cool shaded lounges, and outdoor spaces that feel like private resorts.</p>
<p>But here’s the real truth: stunning outdoor spaces don’t just happen — they’re engineered. And the best landscape contractors in Dubai don’t merely decorate. They build outdoor living environments designed for Dubai’s extreme climate and luxury standards.</p>
<p>Let’s break down what separates an ordinary contractor from an industry leader… and why Hammer Services stands at the top.</p>

<h2>What Makes a Landscape Contractor “The Best” in Dubai?</h2>
<p>The top firms aren’t just designers — they’re engineers, builders, and problem-solvers.</p>
<p>Here’s what they deliver:</p>

<h2>1. Climate-Engineered Hardscapes That Last for Decades</h2>
<p>Paver patios, pathways, driveways, and outdoor flooring must survive brutal heat, shifting sands, and occasional heavy rainfall. The best contractors know which materials perform — and which crack, fade, or warp.</p>

<h2>2. Structures Built for Shade, Strength &amp; Style</h2>
<p>Pergolas, cabanas, and shade systems must be designed with both durability and elegance in mind. A great contractor creates an experience, not just a structure.</p>

<h2>3. Hardscaping That Looks Beautiful Year-Round</h2>
<p>Luxury requires precision. From laser-aligned pavers to clean jointing and drainage planning, craftsmanship determines whether your outdoor space feels premium — or problematic.</p>

<p>And this brings us to the most important point:<br>
<strong>Professionals don’t guess. They diagnose, engineer, and build with intention.</strong></p>

<h2>Why Expertise Isn’t Optional — Especially in Dubai</h2>
<p>Dubai’s unique environment turns small mistakes into expensive disasters.</p>
<p>Here’s what you avoid when you choose a licensed outdoor living contractor instead of a handyman:</p>
<ul>
<li><strong>Heat-resistant materials:</strong> Top contractors understand thermal expansion and choose pavers, stones, and woods that don’t crack or fade.</li>
<li><strong>Drainage engineering:</strong> One unexpected rainfall shouldn’t turn your backyard into a pool. Professionals plan slopes, water channels, and foundations that keep your landscape dry and safe.</li>
<li><strong>Precision installation:</strong> A poorly installed paver doesn’t just look bad — it shifts, sinks, loosens, and drains incorrectly. Quality installation means fewer issues and fewer callbacks.</li>
</ul>

<h2>Why Hire a Professional Landscape Contractor in Dubai?</h2>
<p>DIY seems tempting… until you’re knee-deep in materials, permits, and unexpected problems.</p>
<p>A professional contractor is not an expense — it’s insurance for a stress-free, luxury outcome.</p>

<h2>Flawless Project Management</h2>
<p>A landscape project involves:</p>
<ul>
<li>Municipality permits</li>
<li>Engineering approvals</li>
<li>Vendor coordination</li>
<li>Labor scheduling</li>
<li>Material sourcing</li>
</ul>
<p>Hammer Services handles it all. You get one point of contact — and zero surprises.</p>

<h2>No Permit Issues</h2>
<p>Dubai municipality regulations can be… let’s call it “an experience.” Professionals navigate these rules so you don’t have to.</p>

<h2>No Supplier Delays</h2>
<p>Top contractors work with reliable material suppliers, helping your project stay on schedule.</p>

<h2>No Timeline Surprises</h2>
<p>You get a plan — and it’s actually followed.</p>

<h2>Services Offered by Top Landscape Contractors in Dubai</h2>
<p>If you think landscaping is just plants and grass, let’s reset expectations. Premium firms offer complete outdoor living transformations.</p>

<h2>1. Modern Landscape Architecture &amp; Design</h2>
<p>Where vision becomes blueprint. This includes:</p>
<ul>
<li>3D design renderings</li>
<li>Material selection</li>
<li>Concept-to-construction planning</li>
<li>Functional outdoor zoning</li>
</ul>

<h2>2. Premium Hardscape Installation</h2>
<p>The foundation of all luxury outdoor spaces:</p>
<ul>
<li>Paver driveways &amp; walkways</li>
<li>Outdoor flooring for patios, dining areas, and pools</li>
<li>Custom pathways that move people beautifully through the space</li>
</ul>
<p>Every piece must be precisely engineered — because in Dubai, the ground moves, the heat expands, and only skilled builders know how to compensate.</p>

<h2>3. Outdoor Living Structures</h2>
<p>Where comfort meets architectural beauty. This can include:</p>
<ul>
<li>Pergolas &amp; shade systems</li>
<li>Modern water features</li>
<li>Fountains and cascades</li>
<li>Fire pits &amp; fireplaces</li>
<li>Outdoor kitchens</li>
</ul>
<p>When done right, it feels like a five-star resort — at home.</p>

<h2>Top 8 Landscape Contractors in Dubai (2025 Ranking)</h2>
<p>Updated for performance, reputation, design innovation, and hardscaping excellence.</p>
<p>Below is the expert-level list — and yes, Hammer Services is right where it belongs.</p>
<ul>
<li><strong>1. Hammer Services</strong> — Premium hardscaping, engineered outdoor landscapes, pergolas, water features, paver systems, and full outdoor living design-build. <a href="https://www.hammer-services.com/">https://www.hammer-services.com/</a></li>
<li><strong>2. Cracknell</strong> — Master planning, villa landscaping, luxury garden design.</li>
<li><strong>3. Desert Group</strong> — Sustainable landscaping and environmental solutions.</li>
<li><strong>4. KCJ Landscaping</strong> — Planting, irrigation, lighting, and general landscaping.</li>
<li><strong>5. Green Art Landscape</strong> — Pools, playgrounds, synthetic grass, irrigation.</li>
<li><strong>6. Plantscape UAE</strong> — Vertical gardens, indoor landscaping, garden maintenance.</li>
<li><strong>7. Transgulf</strong> — Architectural solutions and specialised outdoor products.</li>
<li><strong>8. Consent</strong> — Leading manufacturer of concrete products and paver systems.</li>
</ul>

<p>For specialised hardscaping, turnkey outdoor living, and engineered luxury landscapes, Hammer Services is the clear #1.</p>

<h2>Why Hammer Services Stands Above the Rest</h2>
<p>You don’t become the best in Dubai by accident — you earn it.</p>

<h2>1. Engineering-First Approach</h2>
<p>Every project is planned structurally before it’s designed aesthetically. That’s how you get outdoor spaces that look beautiful and last for decades.</p>

<h2>2. Climate-Adaptive Material Selection</h2>
<p>Not all pavers survive the Dubai heat. Not all woods thrive outdoors. Hammer selects materials proven to endure local conditions.</p>

<h2>3. Precision Hardscaping</h2>
<p>The company is known for flawless installation: aligned joints, proper depth, zero shifting, and correct drainage.</p>

<h2>4. End-to-End Project Management</h2>
<p>One team. One vision. One promise: a flawless outdoor living experience.</p>

<h2>FAQs About Hammer Services</h2>

<h2>What makes Hammer Services better than other landscape contractors in Dubai?</h2>
<p>Hammer combines engineering precision with luxury landscaping mastery. They don’t “try things” — they build them right the first time.</p>

<h2>Does Hammer offer free consultations?</h2>
<p>Yes. And it’s not a basic sales call — it’s a professional site assessment where they analyse space constraints, material suitability, structural requirements, and your lifestyle vision. You walk away with real insights — no pressure, no obligation.</p>

<h2>Can Hammer handle complex projects?</h2>
<p>Absolutely. Outdoor kitchens, driveways, large hardscapes, water features, shaded lounges — Hammer manages every moving part.</p>

<h2>How do I start a project with Hammer Services?</h2>
<p>The process is simple and transparent:</p>
<ul>
<li><strong>Contact:</strong> Submit a form or call the Hammer Services team.</li>
<li><strong>Consult:</strong> Discuss vision, materials, and engineering requirements.</li>
<li><strong>Quote:</strong> Receive a detailed, transparent proposal.</li>
<li><strong>Build:</strong> Watch your outdoor space transform into luxury living.</li>
</ul>

<h2>Ready to Build Your Dream Outdoor Space?</h2>
<p>If you want a durable, elegant, and masterfully engineered outdoor environment — without stress, delays, or surprises — you deserve to work with Dubai’s best.</p>
<p><strong>Hammer Services</strong><br>
Dubai’s trusted leader in luxury landscaping &amp; hardscaping.<br>
Start today: <a href="https://www.hammer-services.com/">https://www.hammer-services.com/</a></p>
""",
    },
]


def seed_insights(service_slug: str = "landscape-design-build", reset: bool = False) -> None:
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
        # Truncate excerpt to 240 characters to match database constraint
        excerpt = p["excerpt"][:240] if len(p["excerpt"]) > 240 else p["excerpt"]
        
        # Store tags and categories in blocks metadata for future use
        # (since Insight model only has single tag field with max 40 chars)
        if "tags" in p or "categories" in p:
            if "metadata" not in blocks_data:
                blocks_data["metadata"] = {}
            if "tags" in p:
                blocks_data["metadata"]["tags"] = p["tags"]
            if "categories" in p:
                blocks_data["metadata"]["categories"] = p["categories"]

        obj, was_created = Insight.objects.get_or_create(
            service=svc,
            title=p["title"],
            defaults={
                "slug": slug,
                "tag": p["tag"],
                "read_minutes": p["read_minutes"],
                "excerpt": excerpt,
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
            obj.excerpt = excerpt
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

    parser = argparse.ArgumentParser(
        description="Seed Hammer Services landscape contractor insight for a service"
    )
    parser.add_argument("--service", default="landscape-design-build", help="Service slug")
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Delete existing insights before seeding",
    )
    args = parser.parse_args()

    seed_insights(args.service, args.reset)

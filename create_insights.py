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


# ---- Hammer Services Insights: Landscaping (Trends + Costs) ----
POSTS: t.List[dict] = [
    {
        "title": "2026 Landscaping in Dubai: How Hammer Services Is Raising the Standard for Outdoor Living",
        "tag": "Landscaping",  # Primary tag (max 40 chars)
        "read_minutes": 8,
        "tags": [
            "landscaping Dubai",
            "landscape design Dubai",
            "villa landscaping Dubai",
            "garden design Dubai",
            "pool design Dubai",
            "outdoor living Dubai",
            "design and build Dubai",
            "luxury villa landscaping",
        ],
        "categories": [
            "Outdoor Living",
            "Landscaping",
            "Villa Design",
            "Pools & Water Features",
            "Lighting",
            "Sustainability",
        ],
        "excerpt": (
            "In Dubai, landscaping in 2026 is less about show gardens and more about usable, "
            "climate-smart outdoor rooms. Hammer Services explains how villas are rethinking "
            "shade, pools, lighting and sustainable materials."
        ),
        "cover_image_url": (
            # Swap this for a Hammer / Cloudinary outdoor living hero when ready
            "https://images.unsplash.com/photo-1469796466635-455ede028aca?"
            "w=1600&q=80&auto=format&fit=crop"
        ),
        "body": """
<h1>2026 Landscaping in Dubai: How Hammer Services Is Raising the Standard for Outdoor Living</h1>

<p><strong>Hammer Services Dubai</strong><br>
<em>Category: Landscaping &amp; Outdoor Living</em></p>

<p>Stand in almost any villa community in Dubai today — Dubai Hills, Arabian Ranches, District One, Palm Jumeirah — and the pattern is hard to miss.</p>
<p>The garden is no longer “the space around the house.” For many owners, it is the heart of the home.</p>
<p>Over the past few years, clients have moved from asking for “a lawn and a few trees” to asking questions like: How can we use our garden year-round? Can we entertain outdoors in summer? How do we make the garden match the architecture of the villa?</p>
<p>That shift is what is shaping landscaping in Dubai in 2026.</p>
<p>At Hammer Services, we see this change every day through design consultations, site visits and long-term maintenance. Landscaping is no longer decoration; it is usable living space — and properties with thoughtful landscape design consistently achieve stronger resale value and tenant demand.</p>

<h2>Designing for the Dubai Climate First</h2>
<p>Anyone can draw a pretty garden on paper. The real challenge is making it survive August.</p>
<p>In our recent projects, the starting point is not the pool tile or the furniture style — it is orientation, wind, sun and soil.</p>
<ul>
<li>Which facades take the harsh west sun?</li>
<li>Where can we create natural shade instead of fighting the heat?</li>
<li>How will water move across the site during a rare heavy rainfall?</li>
<li>What does the existing soil and irrigation system look like in reality, not just on a plan?</li>
</ul>
<p>From there, climate-appropriate strategies guide design decisions: shade first, greenery second; drought-tolerant species instead of thirsty exotics; micro-climates around seating, pools and play areas; and irrigation that is efficient rather than wasteful.</p>
<p>Bougainvillea, ghaf, date palms and native grasses continue to outperform imported “show plants” that look good on handover day and struggle a year later. This is where landscape design in Dubai is maturing — from visual landscaping to environmental landscaping.</p>

<h2>Outdoor Living Has Replaced “The Backyard”</h2>
<p>A modern Dubai villa is designed around gatherings — family dinners, children’s birthdays, quiet evenings and weekend barbecues.</p>
<p>The garden is no longer an afterthought. It is now planned as an extension of the living and dining rooms.</p>
<ul>
<li>Outdoor kitchens and BBQ counters for weekends and events</li>
<li>Shaded majlis-style seating that feels like a second living room</li>
<li>Smaller, elegant pools that are actually used, not just photographed</li>
<li>Discreet play zones instead of plastic playground clutter</li>
</ul>
<p>One recent Hammer Services project in Mohammed Bin Rashid City began with a simple brief: “We don’t want a show garden. We want to actually sit outside.”</p>
<p>The final design included a pergola that connected directly to the indoor living space, a plunge pool positioned to catch evening breezes, natural stone paths and layered lighting instead of harsh floodlights. The result was not just beautiful — it was used every single day.</p>
<p>That is the real measure of successful villa landscaping in Dubai.</p>

<h2>Water Features and Pools: Still Iconic, But Smarter</h2>
<p>Pools in Dubai are not trends; they are part of the lifestyle. What is changing is how they are designed.</p>
<p>Instead of oversized rectangles, we see more compact, considered pools that integrate with the architecture and the way the family actually lives.</p>
<ul>
<li>Shallow lounging shelves and in-water seating areas</li>
<li>Darker tiles to improve heat efficiency and visual depth</li>
<li>Cooling, slip-resistant decking materials around the pool</li>
<li>Quiet circulation and filtration systems that do not dominate the space</li>
</ul>
<p>Beyond pools, water is appearing in subtler forms — reflective ponds, narrow rill channels, and low, calming cascades that bring sound and movement into minimalist villas.</p>
<p>This is pool design in Dubai moving away from pure display toward calm, considered luxury that you can feel when you step outside.</p>

<h2>Lighting: Where Most Landscapes Are Won or Lost</h2>
<p>Lighting is usually installed last and, unfortunately, often thought about last. It should be planned at the same time as the layout itself.</p>
<p>When landscape lighting is treated as part of the architecture rather than a utility, the garden transforms after dark.</p>
<ul>
<li>Low garden glows that define planting beds</li>
<li>Warm pathway washes for orientation and safety</li>
<li>Tree uplighting to add height and depth</li>
<li>Discreet step and wall lights to avoid glare</li>
</ul>
<p>The goal is simple: you should want to step outside at night, not feel like you are in a stadium. Done well, lighting makes a villa feel more private, more generous and more inviting, even from the street.</p>

<h2>Integrated Design and Build — One Team, One Vision</h2>
<p>Many homeowners come to us after trying to manage four or five different contractors: a pool company, a softscape company, a separate pergola contractor, an electrician and a handyman for everything else. The result is almost always disjointed.</p>
<p>Hammer Services works differently. A single design-and-build team takes responsibility from concept through approvals, construction and handover.</p>
<ul>
<li>Design consultation and site analysis</li>
<li>3D visualization and material selections</li>
<li>Structural and services coordination</li>
<li>Construction execution and detailing</li>
<li>Post-handover facility management and maintenance</li>
</ul>
<p>That matters because landscaping is not a static product. Plants mature, timber ages, stone weathers and irrigation needs care. A landscape is not “finished” on handover day — it lives and changes.</p>
<p>Having one partner for design, build and aftercare means the space can mature the way it was intended to.</p>

<h2>Sustainability Without the Buzzwords</h2>
<p>“Eco-friendly landscaping” can easily become an empty phrase. In Dubai, genuine sustainability is very practical.</p>
<ul>
<li>Using fewer litres of water per day</li>
<li>Choosing plants that are suited to local climate</li>
<li>Selecting materials that do not fail under heat and UV</li>
</ul>
<p>Vertical gardens, rooftop planting and smart irrigation controllers are all gaining traction, but the biggest sustainability gain is still simple: right plant, right place.</p>
<p>That reduces replacements, transport, waste and labour — and keeps gardens looking healthy without constant intervention.</p>

<h2>Why Clients Choose Hammer Services</h2>
<p>Hammer Services is not a budget landscaping company. Clients approach us because they want design clarity, engineering competence and a consistent language between interior and exterior spaces.</p>
<p>Our multidisciplinary background in landscape design, interior design, luxury villa construction and facility management means we treat outdoor space as part of the architecture, not an afterthought.</p>
<p>In practice, that looks like:</p>
<ul>
<li>Landscaping that matches the villa’s architecture and interior palette</li>
<li>Details that feel considered, from paver layouts to step heights</li>
<li>Materials chosen for Dubai, not copied from another climate</li>
<li>Clear communication on timelines, phasing and budget</li>
</ul>

<h2>Closing Thoughts</h2>
<p>Landscaping in Dubai in 2026 is moving toward something more mature and more honest.</p>
<p>Less show. More use. Less maintenance burden. More climate-aware design.</p>
<p>If your goal is not just to “green your villa” but to create an outdoor room you will actually live in, design matters — and execution matters even more.</p>
<p>Hammer Services’ role is straightforward: to design responsibly, build precisely and care for landscapes long after the last plant is installed.</p>
<p>For homeowners who see their garden as part of their lifestyle, not just part of their plot, that partnership makes all the difference.</p>
""",
    },
    {
        "title": "How Much Does Villa Landscaping Cost in Dubai in 2026? A Practical Homeowner’s Guide",
        "tag": "Costs & Budgeting",  # Primary tag (max 40 chars)
        "read_minutes": 9,
        "tags": [
            "landscaping cost Dubai",
            "villa landscaping cost Dubai",
            "garden design cost Dubai",
            "landscape design Dubai prices",
            "landscaping Dubai 2026",
            "outdoor living budget Dubai",
            "pool and landscaping cost Dubai",
        ],
        "categories": [
            "Landscaping",
            "Costs & Budgeting",
            "Outdoor Living",
            "Villa Design",
        ],
        "excerpt": (
            "Wondering how much villa landscaping costs in Dubai in 2026? This guide breaks down "
            "realistic budget ranges for softscape, hardscape, pools, lighting and maintenance — "
            "so you can plan your garden transformation with confidence."
        ),
        "cover_image_url": (
            "https://images.unsplash.com/photo-1500534314211-0a24cd03f2c0?"
            "w=1600&q=80&auto=format&fit=crop"
        ),
        "body": """
<h1>How Much Does Villa Landscaping Cost in Dubai in 2026? A Practical Homeowner’s Guide</h1>

<p><strong>Hammer Services Dubai</strong><br>
<em>Category: Landscaping Costs &amp; Budget Planning</em></p>

<p>One of the first questions almost every villa owner asks us is simple:</p>
<p><strong>“How much will it actually cost to landscape my villa in Dubai?”</strong></p>

<p>It’s a fair question — but the honest answer is, “It depends on what you want this space to do for you.”</p>
<p>Landscaping in Dubai in 2026 can range from a modest refresh of planting and pathways all the way to a full outdoor living upgrade with pool, pergola, outdoor kitchen, lighting and smart irrigation.</p>
<p>This guide won’t give you a one-line price. Instead, it will help you understand the <strong>key cost drivers</strong>, <strong>realistic budget ranges</strong>, and the <strong>mistakes that make projects more expensive than they need to be</strong>.</p>

<h2>What Drives Landscaping Cost in Dubai?</h2>
<p>When we prepare a proposal at Hammer Services, we look at a few core factors before we even talk numbers:</p>
<ul>
<li><strong>Plot size and usable garden area</strong> – front, back and side setbacks all matter.</li>
<li><strong>Existing conditions</strong> – is there old paving to remove, poor soil, or drainage issues?</li>
<li><strong>Scope of work</strong> – softscape only, or full hardscape, pool, pergola and outdoor kitchen?</li>
<li><strong>Material level</strong> – standard, premium or high-end imported finishes?</li>
<li><strong>Access and logistics</strong> – can machinery get in easily, or is everything manual?</li>
</ul>
<p>Two villas with the same plot size can have very different costs depending on these details.</p>

<h2>Typical Budget Ranges for Villa Landscaping in Dubai (2026)</h2>
<p>Every project is unique, but most homeowners we speak to fall into one of these three broad categories:</p>

<h3>1. Essential Refresh: “Clean, Green and Usable”</h3>
<p>This is for owners who want the garden to feel finished and tidy without turning it into a resort.</p>
<ul>
<li>Basic planting with climate-appropriate trees, shrubs and groundcovers</li>
<li>Lawn (natural or artificial) for children or pets</li>
<li>Simple paver or tile pathways</li>
<li>Entry planting to enhance curb appeal</li>
<li>Basic garden lighting for safety</li>
</ul>
<p>Ideal for new handovers where the priority is to make the exterior <strong>presentable and practical</strong> without major structural work.</p>

<h3>2. Outdoor Living Upgrade: “We Actually Want to Use This”</h3>
<p>This is the most common scope for villa landscaping in Dubai. The goal is to create an outdoor room that feels like part of the house.</p>
<ul>
<li>Pergola or shaded seating area connected to the main living/dining zones</li>
<li>Feature planting with layered heights and textures</li>
<li>Quality pavers or porcelain tiles for terraces and walkways</li>
<li>Integrated garden lighting for evening use</li>
<li>Possibly a small water feature or plunge pool</li>
</ul>
<p>This is where thoughtful <strong>landscape design in Dubai</strong> pays off — the difference between “plants around the perimeter” and a garden you actually live in.</p>

<h3>3. Full Resort-Style Landscape: “Our Home Is Our Weekend Destination”</h3>
<p>For some clients, the villa is meant to feel like a private boutique resort.</p>
<ul>
<li>Custom swimming pool or lap pool with lighting and water features</li>
<li>Large pergolas, cabanas or outdoor majlis areas</li>
<li>Outdoor kitchen / BBQ island with storage and services</li>
<li>Premium hardscape (natural stone, high-end porcelain, feature walls)</li>
<li>Advanced lighting design and smart controls</li>
<li>Vertical gardens, feature trees and accent planting</li>
</ul>
<p>These projects require more structural work, engineering and coordination — and the final result completely changes how the property feels and functions.</p>

<h2>Softscape vs Hardscape: Where Does the Money Go?</h2>
<p>Many owners are surprised to learn that plants are not the most expensive part of a landscaping budget.</p>
<p>A typical villa landscaping budget in Dubai is often dominated by <strong>hardscape and structures</strong>:</p>
<ul>
<li>Pavers, tiles and concrete works</li>
<li>Pool construction and mechanical systems</li>
<li>Pergolas, seating walls and built-in planters</li>
<li>Outdoor kitchens and counters</li>
</ul>
<p>Softscape — trees, shrubs, groundcovers and soil preparation — is crucial for the look and feel, but structurally and financially, hardscape is usually the backbone of the project.</p>

<h2>Hidden Costs Homeowners Often Forget</h2>
<p>There are a few line items that can surprise first-time villa owners:</p>
<ul>
<li><strong>Demolition and removal</strong> – breaking and disposing of old tiles, concrete and poorly built features.</li>
<li><strong>Upgrading irrigation</strong> – retrofitting systems that were never designed for the new layout.</li>
<li><strong>Drainage corrections</strong> – fixing slopes so water flows away from the villa, not towards it.</li>
<li><strong>Temporary access and protection</strong> – especially in tightly planned communities.</li>
</ul>
<p>At Hammer Services, we prefer to surface these items early so budgets are realistic from the beginning.</p>

<h2>How to Plan a Realistic Landscaping Budget in Dubai</h2>
<p>If you are planning to landscape your villa in 2026, here is a simple sequence that keeps things under control:</p>
<ul>
<li><strong>1. Define the outcome, not the materials.</strong> Start with how you want to use the space: kids’ play, entertaining, quiet evenings, pool, pets, etc.</li>
<li><strong>2. Set a budget range, not a random number.</strong> Decide if you are closer to an essential refresh, an outdoor living upgrade or a full resort-style transformation.</li>
<li><strong>3. Get a proper site assessment.</strong> A quick WhatsApp ballpark is not a design; a site visit and drawings will save you money later.</li>
<li><strong>4. Phase if needed.</strong> Good designers can plan a master layout that you implement in stages without wasting work.</li>
</ul>

<h2>Why Work with Hammer Services on Budget-Sensitive Projects?</h2>
<p>Because we design, build and maintain landscapes, we see the full life cycle of outdoor spaces — including what fails early and what performs well for years.</p>
<p>That experience shapes how we talk about cost:</p>
<ul>
<li>We are honest if a budget is too low for the desired outcome.</li>
<li>We suggest where to invest (structure and layout) and where you can be more economical (some finishes and furnishings).</li>
<li>We design with future maintenance in mind, so you are not paying for constant fixes.</li>
</ul>
<p>The goal is not to create the most expensive garden on the street. The goal is to create a landscape that matches your villa, your lifestyle and your long-term plans.</p>

<h2>Next Step: Get Numbers That Match Your Villa</h2>
<p>Online guides are helpful, but there is no substitute for a tailored proposal based on your actual plot, community guidelines and priorities.</p>
<p>If you are considering landscaping your villa in Dubai in 2026, Hammer Services can:</p>
<ul>
<li>Visit your property and assess existing conditions</li>
<li>Prepare a concept aligned with your budget range</li>
<li>Provide a transparent breakdown of key cost areas</li>
<li>Offer options for phasing the work if needed</li>
</ul>

<p><strong>Hammer Services</strong><br>
Landscape design, build and maintenance for Dubai villas.<br>
Start a conversation today and find out what is realistically possible for your budget.</p>
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
        description="Seed Hammer Services landscaping insights for a service"
    )
    parser.add_argument("--service", default="landscape-design-build", help="Service slug")
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Delete existing insights before seeding",
    )
    args = parser.parse_args()

    seed_insights(args.service, args.reset)

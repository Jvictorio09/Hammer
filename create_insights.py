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
    """
    Make a globally-unique slug for Insight by suffixing -2, -3, ...
    """
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
    """
    Convert HTML content to Editor.js blocks format.
    """
    if not html_content or not html_content.strip():
        return {
            "time": int(timezone.now().timestamp() * 1000),
            "blocks": [],
            "version": "2.28.2",
        }

    blocks = []
    lines = html_content.split("\n")

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Handle headings
        if line.startswith("<h1>"):
            text = re.sub(r"<[^>]+>", "", line).strip()
            if text:
                blocks.append({
                    "id": str(uuid.uuid4()),
                    "type": "header",
                    "data": {"text": text, "level": 1},
                })
        elif line.startswith("<h2>"):
            text = re.sub(r"<[^>]+>", "", line).strip()
            if text:
                blocks.append({
                    "id": str(uuid.uuid4()),
                    "type": "header",
                    "data": {"text": text, "level": 2},
                })
        elif line.startswith("<h3>"):
            text = re.sub(r"<[^>]+>", "", line).strip()
            if text:
                blocks.append({
                    "id": str(uuid.uuid4()),
                    "type": "header",
                    "data": {"text": text, "level": 3},
                })
        elif line.startswith("<h4>"):
            text = re.sub(r"<[^>]+>", "", line).strip()
            if text:
                blocks.append({
                    "id": str(uuid.uuid4()),
                    "type": "header",
                    "data": {"text": text, "level": 4},
                })
        elif line.startswith("<h5>"):
            text = re.sub(r"<[^>]+>", "", line).strip()
            if text:
                blocks.append({
                    "id": str(uuid.uuid4()),
                    "type": "header",
                    "data": {"text": text, "level": 5},
                })
        elif line.startswith("<h6>"):
            text = re.sub(r"<[^>]+>", "", line).strip()
            if text:
                blocks.append({
                    "id": str(uuid.uuid4()),
                    "type": "header",
                    "data": {"text": text, "level": 6},
                })

        # Handle blockquotes
        elif line.startswith("<blockquote>"):
            text = re.sub(r"<[^>]+>", "", line).strip()
            if text:
                blocks.append({
                    "id": str(uuid.uuid4()),
                    "type": "quote",
                    "data": {"text": text, "caption": ""},
                })

        # Handle lists (simplified)
        elif line.startswith("<ul>"):
            # Simplified approach—nested lists not parsed here
            continue
        elif line.startswith("<li>"):
            text = re.sub(r"<[^>]+>", "", line).strip()
            if text:
                blocks.append({
                    "id": str(uuid.uuid4()),
                    "type": "list",
                    "data": {"style": "unordered", "items": [text]},
                })

        # Handle paragraphs
        elif line.startswith("<p>"):
            text = re.sub(r"<[^>]+>", "", line).strip()
            if text:
                blocks.append({
                    "id": str(uuid.uuid4()),
                    "type": "paragraph",
                    "data": {"text": text},
                })

        # Fallback: plain text → paragraph
        elif line and not line.startswith("<"):
            blocks.append({
                "id": str(uuid.uuid4()),
                "type": "paragraph",
                "data": {"text": line},
            })

    return {
        "time": int(timezone.now().timestamp() * 1000),
        "blocks": blocks,
        "version": "2.28.2",
    }


# ---- New Hammer Landscape Insights (HTML bodies) ----
# NOTE: Keep within fields existing on your Insight model:
# title, slug, tag, read_minutes, excerpt, cover_image_url, body,
# published, published_at. If your model uses different field names,
# adjust below accordingly.

POSTS: t.List[dict] = [
    {
        "title": "Transforming Dubai Villas into Outdoor Sanctuaries: Modern Landscape Design Trends for 2025",
        "tag": "Trends",
        "read_minutes": 6,
        "excerpt": (
            "Discover the latest landscape design trends in Dubai for 2025 — "
            "from sustainable gardens and water-smart irrigation to biophilic design."
        ),
        "cover_image_url": (
            "https://images.unsplash.com/photo-1519710164239-da123dc03ef4?"
            "w=1600&q=80&auto=format&fit=crop"
        ),
        "body": """
<h1>Transforming Dubai Villas into Outdoor Sanctuaries: Modern Landscape Design Trends for 2025</h1>
<p><em>Meta Description:</em> Discover the latest <strong>landscape design trends in Dubai for 2025</strong> — from sustainable gardens and water-smart irrigation to biophilic design. Create your dream villa landscape with Hammer Landscape.</p>

<h2>The Rise of Outdoor Living in Dubai</h2>
<p>Dubai homeowners are redefining luxury. No longer limited to lavish interiors, the modern villa lifestyle extends seamlessly into the outdoors. Gardens are becoming personal sanctuaries — spaces for morning coffee, family gatherings, or peaceful evenings under the stars.</p>
<p>As 2025 unfolds, <strong>landscape design in Dubai</strong> is shifting toward natural beauty, sustainability, and sensory experiences that turn every villa into a private resort.</p>

<h2>1. Sustainable Luxury: Greener Choices for a Greener Future</h2>
<p>In a city known for its innovation, sustainability has become the new standard of elegance. Modern villa landscaping now embraces <strong>eco-friendly materials</strong>, <strong>solar lighting</strong>, and <strong>automated irrigation systems</strong> that conserve water while keeping gardens lush year-round.</p>
<p>At Hammer Landscape, we design with intention — balancing aesthetics and ecology. Our team uses <strong>permeable paving</strong>, <strong>locally sourced stone</strong>, and <strong>smart plant selection</strong> that thrives in Dubai’s climate without excess maintenance.</p>
<blockquote>Because true luxury is effortless — and kind to the environment.</blockquote>

<h2>2. Water-Wise Gardens that Bloom All Year</h2>
<p>Water is life — and in Dubai, it’s precious. The trend of <strong>water-wise gardens</strong> combines drought-resistant plants like <em>bougainvillea</em>, <em>desert rose</em>, and ornamental grasses with efficient drip irrigation systems.</p>
<p>By rethinking how water flows through your outdoor space, you can create a <strong>vibrant, low-maintenance garden</strong> that stays beautiful even under the summer sun.</p>
<p>Our experts at Hammer Landscape specialize in <strong>hydrozoning</strong> — grouping plants with similar water needs — so every drop counts.</p>

<h2>3. Biophilic Design: Bringing Nature Closer to Home</h2>
<p>Biophilic design, a major 2025 trend, focuses on connecting humans and nature. Think <strong>vertical green walls</strong>, <strong>shaded pergolas</strong> with climbing vines, and <strong>stone pathways</strong> that lead to tranquil water features.</p>
<p>These natural elements don’t just look beautiful — they reduce stress, improve air quality, and elevate your overall sense of well-being.</p>
<p>Imagine walking barefoot across soft grass, surrounded by greenery that feels alive and personal. That’s not just landscaping — that’s <strong>healing design</strong>.</p>

<h2>4. Smart Technology Meets Outdoor Elegance</h2>
<p>Innovation isn’t just for smart homes anymore. From <strong>app-controlled lighting systems</strong> to <strong>climate-responsive irrigation</strong>, Dubai’s villas are embracing intelligent landscapes that adapt to your lifestyle.</p>
<p>You can now schedule lighting scenes for evening dinners or control fountains and pool features directly from your phone — blending modern convenience with timeless ambiance.</p>
<p>Hammer Landscape brings this future-ready vision to life, ensuring technology enhances the art of outdoor living, never replaces it.</p>

<h2>5. Personalized Outdoor Experiences</h2>
<p>Every villa tells a story — and your landscape should too. Whether it’s a <strong>Zen-inspired courtyard</strong>, a <strong>Mediterranean poolside retreat</strong>, or a <strong>family-friendly garden</strong>, personalization is the final touch that defines 2025 design.</p>
<p>We collaborate closely with clients to craft spaces that feel uniquely yours — functional, beautiful, and perfectly balanced with Dubai’s modern architectural rhythm.</p>

<h2>Your Outdoor Sanctuary Awaits</h2>
<p>If you’ve been dreaming of a serene, resort-style escape right outside your villa doors, 2025 is the year to make it happen.</p>
<p><strong>Hammer Landscape</strong> brings together design innovation, craftsmanship, and local expertise to transform outdoor spaces into timeless works of art.</p>
<p>🌿 <strong>Let’s create your sanctuary today.</strong> <a href="/contact" class="btn btn-primary">Contact Hammer Landscape</a> for a consultation and start your villa transformation.</p>
""",
    },
    {
        "title": "The Secret to a Low-Maintenance Garden in Dubai’s Climate",
        "tag": "Guides",
        "read_minutes": 7,
        "excerpt": (
            "Low-maintenance garden ideas for Dubai: desert-friendly plants, smart irrigation, "
            "and clever design to keep your garden lush with minimal effort."
        ),
        "cover_image_url": (
            "https://images.unsplash.com/photo-1523413651479-597eb2da0ad6?"
            "w=1600&q=80&auto=format&fit=crop"
        ),
        "body": """
<h1>The Secret to a Low-Maintenance Garden in Dubai’s Climate</h1>
<p><em>Meta Description:</em> Looking for <strong>low-maintenance garden ideas in Dubai</strong>? Learn how desert-friendly plants, smart irrigation, and clever design can keep your garden lush year-round with minimal effort — powered by Hammer Landscape.</p>

<h2>The Dubai Garden Dilemma</h2>
<p>Dubai is a city of contrasts — sleek skyscrapers, golden deserts, and stunning villas with private gardens. But while the dream of lush greenery is alive and well, the reality is that Dubai’s heat and arid climate make garden maintenance a real challenge.</p>
<p>Between scorching summers, high water costs, and limited time, many homeowners ask the same question:
<strong>“Can I have a beautiful garden that doesn’t demand constant care?”</strong></p>
<p>The answer is yes — and it starts with smart design.</p>

<h2>1. Choose Plants That Thrive, Not Just Survive</h2>
<p>The foundation of any <em>low-maintenance garden in Dubai</em> lies in plant selection. Native and adaptive species can flourish in the UAE climate with far less watering and upkeep.</p>
<ul>
  <li><strong>Bougainvillea</strong> – vibrant color with minimal care.</li>
  <li><strong>Desert Rose (Adenium)</strong> – striking blooms, drought-resistant.</li>
  <li><strong>Fountain Grass</strong> – adds movement and texture.</li>
  <li><strong>Date Palm</strong> – timeless Dubai classic that handles heat beautifully.</li>
</ul>
<p>At <strong>Hammer Landscape</strong>, we design plant palettes that are both aesthetically rich and environmentally sensible — ensuring beauty without burden.</p>

<h2>2. Smart Irrigation: Let Technology Do the Work</h2>
<p>With <strong>smart irrigation systems</strong>, you can automate your garden care using sensors, timers, and weather-based controls that adjust watering based on actual conditions.</p>
<ul>
  <li>Up to <strong>40% water savings</strong> annually.</li>
  <li>Healthier root systems (no overwatering).</li>
  <li>Remote control via mobile app — ideal for busy villa owners or frequent travelers.</li>
</ul>
<p>We integrate <strong>drip irrigation</strong> networks that deliver moisture directly to roots — not wasted on evaporation. Your garden stays hydrated, not high-maintenance.</p>

<h2>3. Design for Shade and Efficiency</h2>
<p>Strategic shade from <strong>pergolas</strong>, <strong>trees</strong>, or <strong>architectural screens</strong> reduces soil temperature and prevents plant stress.</p>
<p>Meanwhile, <strong>mulching</strong> (organic or decorative gravel) locks in soil moisture and minimizes weeds. The result? A garden that practically takes care of itself.</p>
<p>Hammer Landscape specializes in layouts that maximize shade, airflow, and efficiency — giving your garden resilience through every season.</p>

<h2>4. Go Minimal, Go Modern</h2>
<p>Modern <strong>landscape design in Dubai</strong> is leaning toward structured minimalism — clean lines, sculptural plants, and simple geometric layouts. Think fewer elements, more impact.</p>

<h2>5. Add Automated Lighting and Seasonal Timers</h2>
<p><strong>Solar/LED smart lighting</strong> can be programmed to turn on at sunset, highlight pathways, or create a warm glow — all without lifting a finger. It’s beauty on autopilot.</p>

<h2>Your Garden, Simplified — by Design</h2>
<p>At <strong>Hammer Landscape</strong>, we believe elegance should feel effortless. We create sustainable, low-maintenance outdoor spaces that thrive in Dubai’s unique climate — so you can simply relax and enjoy your garden.</p>
<p>💧 <strong>Let’s build your low-maintenance oasis.</strong> <a href="/contact" class="btn btn-primary">Contact Hammer Landscape</a> to start designing a garden that’s as smart as it is stunning.</p>
""",
    },
    {
        "title": "Outdoor Living Elevated: Why Pergolas and Pools Are the New Must-Haves for Dubai Homes",
        "tag": "Outdoor Living",
        "read_minutes": 6,
        "excerpt": (
            "Why pergolas and pools are transforming outdoor living in Dubai — comfort, style, "
            "and property value in one integrated design."
        ),
        "cover_image_url": (
            "https://images.unsplash.com/photo-1505693416388-ac5ce068fe85?"
            "w=1600&q=80&auto=format&fit=crop"
        ),
        "body": """
<h1>Outdoor Living Elevated: Why Pergolas and Pools Are the New Must-Haves for Dubai Homes</h1>
<p><em>Meta Description:</em> Discover why <strong>pergolas and pools</strong> are transforming outdoor living in Dubai. Learn how modern <strong>pergola design</strong> and <strong>pool landscaping</strong> boost comfort, style, and property value with Hammer Landscape.</p>

<h2>The New Definition of Home Luxury</h2>
<p>In Dubai, luxury no longer stops at the front door. Today’s homeowners crave outdoor spaces that feel like private resorts — places where design, comfort, and functionality flow seamlessly together.</p>
<p>Whether it’s sipping coffee under a shaded pergola or cooling off in a crystal-clear pool, <strong>outdoor living</strong> has become the heartbeat of modern villa life.</p>
<p>At Hammer Landscape, we see it every day: transforming an underused yard into a lifestyle destination instantly elevates both mood and market value.</p>

<h2>1. Pergolas: The Art of Shade and Style</h2>
<p>Pergolas are more than architectural accents — they’re the soul of outdoor living. Designed to provide shade, structure, and sophistication, a pergola defines space without confining it.</p>
<p>Modern <strong>pergola design in Dubai</strong> blends natural wood tones, aluminum finishes, and <strong>motorized louver roofs</strong> that adjust sunlight with a tap. Add soft lighting, ceiling fans, and greenery for a retreat that works from sunrise to midnight.</p>
<blockquote>Shade, serenity, and style — all in one elegant frame.</blockquote>

<h2>2. Pools: The Centerpiece of Outdoor Life</h2>
<p>No Dubai villa is complete without the sparkle of a pool. Beyond leisure, <strong>modern pool landscaping</strong> turns this feature into a design statement — infinity edges, natural stone borders, LED lighting, and lush privacy planting.</p>
<p>Smart systems now allow temperature control and cleaning automation via smartphone — low effort, high enjoyment.</p>

<h2>3. The Power of Integration: Pergola + Pool Harmony</h2>
<p>Together, pergolas and pools create the perfect outdoor ecosystem — shaded dining by the water, sunset lounges, or a private cabana that feels five-star. Hammer Landscape crafts transitions so seamless that your backyard feels like one cohesive experience.</p>

<h2>4. Outdoor Design as an Investment</h2>
<p>Dubai’s real estate experts agree: <strong>landscape upgrades can raise property value by up to 20%</strong>. A well-designed pool and pergola not only attract buyers but also enhance daily living.</p>

<h2>5. Details That Define 2025</h2>
<ul>
  <li>Solar-powered lighting for energy efficiency.</li>
  <li>Natural materials like teak and limestone.</li>
  <li>Desert-friendly greenery for effortless upkeep.</li>
  <li>Smart irrigation and climate-responsive shading.</li>
</ul>

<h2>Let’s Build Your Resort at Home</h2>
<p>From concept sketches to final construction, <strong>Hammer Landscape</strong> turns your vision into a beautifully livable outdoor masterpiece.</p>
<p>🪵 <strong>Pergolas that breathe sophistication. Pools that inspire serenity.</strong> Together, they create a lifestyle you’ll never want to leave. <a href="/contact" class="btn btn-primary">Contact Hammer Landscape</a> to start your villa transformation.</p>
""",
    },
    {
        "title": "From Sand to Sanctuary: How Professional Landscaping Increases Your Property’s Value",
        "tag": "Strategy",
        "read_minutes": 6,
        "excerpt": (
            "How professional landscaping in Dubai boosts property value, beauty, and livability — "
            "the smart upgrade for homeowners and developers."
        ),
        "cover_image_url": (
            "https://images.unsplash.com/photo-1501183638710-841dd1904471?"
            "w=1600&q=80&auto=format&fit=crop"
        ),
        "body": """
<h1>From Sand to Sanctuary: How Professional Landscaping Increases Your Property’s Value</h1>
<p><em>Meta Description:</em> Discover how professional <strong>landscaping in Dubai</strong> can boost your property’s value, beauty, and livability. Learn why working with expert <strong>landscape contractors in Dubai</strong> turns your villa into a timeless sanctuary.</p>

<h2>Where Aesthetics Meet Investment</h2>
<p>In Dubai’s fast-evolving property market, design isn’t just about style — it’s about strategy. The most successful homeowners and developers understand that <strong>landscaping is a value multiplier</strong>.</p>
<p>Whether you’re selling, leasing, or simply elevating your lifestyle, a professionally designed outdoor space doesn’t just attract admiration — it attracts <em>returns</em>.</p>

<h2>1. First Impressions That Sell</h2>
<p>A well-designed landscape acts as a visual handshake — communicating care, quality, and refinement before a visitor ever steps inside. Lush greenery, balanced symmetry, and thoughtful lighting create a feeling of welcome and worth.</p>

<h2>2. The ROI of Outdoor Design</h2>
<p>According to property experts, <strong>landscaping can boost resale value by 15–20%</strong> — especially in luxury markets like Dubai, where outdoor living defines lifestyle. From bespoke pergolas and custom pools to minimalist courtyards, professional landscaping adds tangible appeal and function.</p>

<h2>3. Smart Design for Harsh Climates</h2>
<p>Dubai’s environment demands strategic planning — from <strong>plant selection</strong> and <strong>irrigation systems</strong> to <strong>heat-resistant materials</strong>. Our team designs with longevity in mind: native and drought-tolerant plants, smart irrigation to optimize usage, and shade solutions that enhance comfort and reduce cooling costs.</p>

<h2>4. Beyond Greenery: Creating Livable Luxury</h2>
<p>Modern landscaping is about creating experiences that extend living areas outward — elegant lounges under pergolas, alfresco dining beside shimmering pools, and warm pathway lighting that invites evening strolls.</p>

<h2>5. The Professional Edge</h2>
<p>DIY can’t compete with professional insight. A cohesive design requires understanding architecture, microclimate, drainage, materials, and human flow. Hammer Landscape’s design-build specialists handle everything — from concept to completion — to yield lasting returns.</p>

<h2>Elevate Your Property, Elevate Your Life</h2>
<p>In Dubai, beauty is currency — and your landscape is your signature. Whether you’re a homeowner seeking serenity or a developer aiming for distinction, a well-executed outdoor design is the smartest upgrade you can make.</p>
<p>🌸 <strong>From sand to sanctuary, Hammer Landscape builds value that lasts.</strong> <a href="/contact" class="btn btn-primary">Contact Hammer Landscape</a> to start your transformation.</p>
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

        # Convert HTML body to Editor.js blocks
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
                "body": p["body"].strip(),  # Keep original HTML for reference
                "blocks": blocks_data,      # Add Editor.js blocks
                "published": True,
                "published_at": timezone.now(),
            },
        )
        if was_created:
            created += 1
        else:
            # If a record with same title exists and reset wasn't used, update it
            obj.tag = p["tag"]
            obj.read_minutes = p["read_minutes"]
            obj.excerpt = p["excerpt"]
            obj.cover_image_url = p["cover_image_url"]
            obj.body = p["body"].strip()
            obj.blocks = blocks_data  # Update blocks too
            obj.published = True
            if not obj.published_at:
                obj.published_at = timezone.now()
            obj.save()

    total = Insight.objects.filter(service=svc).count()
    print(f"Seeded/updated {created} insights for '{service_slug}'. Total now: {total}.")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Seed Hammer Landscape insights for a service")
    parser.add_argument("--service", default="landscape-design-build", help="Service slug")
    parser.add_argument("--reset", action="store_true", help="Delete existing insights before seeding")
    args = parser.parse_args()

    seed_insights(args.service, args.reset)

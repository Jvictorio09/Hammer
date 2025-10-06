# create_insights.py
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

from myApp.models import Service, Insight


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
    Convert a simple HTML subset to Editor.js blocks.
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

        # Headings
        if line.startswith("<h1>"):
            text = re.sub(r"<[^>]+>", "", line).strip()
            blocks.append({"id": str(uuid.uuid4()), "type": "header", "data": {"text": text, "level": 1}})
        elif line.startswith("<h2>"):
            text = re.sub(r"<[^>]+>", "", line).strip()
            blocks.append({"id": str(uuid.uuid4()), "type": "header", "data": {"text": text, "level": 2}})
        elif line.startswith("<h3>"):
            text = re.sub(r"<[^>]+>", "", line).strip()
            blocks.append({"id": str(uuid.uuid4()), "type": "header", "data": {"text": text, "level": 3}})

        # Blockquotes
        elif line.startswith("<blockquote>"):
            text = re.sub(r"<[^>]+>", "", line).strip()
            blocks.append({"id": str(uuid.uuid4()), "type": "quote", "data": {"text": text, "caption": ""}})

        # Lists (simplified: one block per <li>)
        elif line.startswith("<ul>") or line.startswith("<ol>"):
            continue
        elif line.startswith("<li>"):
            text = re.sub(r"<[^>]+>", "", line).strip()
            blocks.append({"id": str(uuid.uuid4()), "type": "list", "data": {"style": "unordered", "items": [text]}})

        # Paragraphs
        elif line.startswith("<p>"):
            text = re.sub(r"<[^>]+>", "", line).strip()
            blocks.append({"id": str(uuid.uuid4()), "type": "paragraph", "data": {"text": text}})

        # Fallback: plain text
        elif line and not line.startswith("<"):
            blocks.append({"id": str(uuid.uuid4()), "type": "paragraph", "data": {"text": line}})

    return {"time": int(timezone.now().timestamp() * 1000), "blocks": blocks, "version": "2.28.2"}


# ---- Hammer Facility Insights (HTML bodies) ----
POSTS: t.List[dict] = [
    {
        "title": "Facility Management in Dubai: The Ultimate Preventive Maintenance Checklist for Villas & Commercial Spaces",
        "tag": "Checklist",
        "read_minutes": 8,
        "excerpt": "A Dubai-specific preventive maintenance checklist for villas and commercial properties—HVAC, MEP, pools, life-safety, and envelope care.",
        "cover_image_url": "https://images.unsplash.com/photo-1581090124361-0f3b7f5b2b54?w=1600&q=80&auto=format&fit=crop",
        "body": """
<h1>Facility Management in Dubai: The Ultimate Preventive Maintenance Checklist for Villas & Commercial Spaces</h1>
<p><em>Meta Description:</em> Cut downtime and costs with this <strong>preventive maintenance checklist for Dubai properties</strong>. From HVAC and MEP to pools and life-safety systems, Hammer Facility’s in-house team keeps villas and commercial spaces running flawlessly.</p>

<h2>Why Preventive Beats Reactive (Every. Single. Time.)</h2>
<p>In Dubai’s climate, heat + dust + humidity = accelerated wear. Waiting for things to break is the most expensive way to run a property. <strong>Preventive maintenance</strong> extends asset life, reduces emergency call-outs, and stabilizes energy bills—whether you manage a private villa or a multi-tenant commercial site.</p>

<h3>Quick wins you’ll feel within 90 days:</h3>
<ul>
  <li>Fewer breakdowns and tenant complaints</li>
  <li>Lower energy consumption (clean coils, balanced airflows, correct setpoints)</li>
  <li>Longer equipment life (bearings, belts, pumps, motors)</li>
  <li>Safer, compliant operations</li>
</ul>

<h2>The Master Checklist (Dubai Edition)</h2>
<p><em>Use this as a baseline. Hammer Facility customizes task lists per asset register, OEM manuals, and occupancy profile.</em></p>

<h3>1) HVAC (Chillers / Package Units / DX Splits / FCUs)</h3>
<p><strong>Weekly / Monthly</strong></p>
<ul>
  <li>Clean or replace filters; log ΔP across filters</li>
  <li>Inspect condensate drains; clear algae &amp; check traps</li>
  <li>Wipe return/supply grilles; remove dust buildup</li>
  <li>Verify thermostat setpoints (villas: 23–24°C typical)</li>
  <li>Listen for abnormal fan/motor noise; check belt tension</li>
</ul>
<p><strong>Quarterly</strong></p>
<ul>
  <li>Deep clean coils (evaporator &amp; condenser); straighten fins</li>
  <li>Check refrigerant pressures vs. OEM charts; inspect for leaks</li>
  <li>Calibrate sensors (temp, humidity, CO₂ where applicable)</li>
  <li>Test actuators and VFDs; verify airflow &amp; balancing</li>
  <li>Inspect insulation for sweating/condensation</li>
</ul>
<p><strong>Annually</strong></p>
<ul>
  <li>Overhaul FCUs/AHUs (bearings, shafts, dampers)</li>
  <li>Service chiller/condensing units; oil analysis where applicable</li>
  <li>Validate BMS sequences (schedules, set-backs, alarms)</li>
</ul>

<h3>2) Electrical Systems</h3>
<p><strong>Monthly</strong></p>
<ul>
  <li>Thermal scan of DBs/MCCs (hot spots = loose lugs)</li>
  <li>Test RCD/RCBO trip operation; verify labeling</li>
  <li>Check emergency/exit lights; replace failures</li>
  <li>Inspect UPS/inverter health &amp; battery runtime</li>
</ul>
<p><strong>Quarterly</strong></p>
<ul>
  <li>Tighten terminations; clean panels; torque to spec</li>
  <li>Load-test generators (commercial); exercise under load</li>
</ul>
<p><strong>Annually</strong></p>
<ul>
  <li>Comprehensive earthing test, insulation resistance tests</li>
  <li>Full single-line diagram review and update after any changes</li>
</ul>

<h3>3) Plumbing &amp; Water Systems</h3>
<p><strong>Monthly</strong></p>
<ul>
  <li>Inspect pumps (pressure/flow, vibration, seal leaks)</li>
  <li>Check water tanks (levels, lids, screens, cleanliness)</li>
  <li>Test mixing valves; verify stable hot-water delivery</li>
</ul>
<p><strong>Quarterly</strong></p>
<ul>
  <li>Descale aerators and showerheads; clean strainers</li>
  <li>Flush low-use outlets to maintain water quality</li>
</ul>
<p><strong>Annually</strong></p>
<ul>
  <li>Tank cleaning &amp; disinfection (per local best practices)</li>
  <li>Service water heaters/heat exchangers; replace anodes</li>
</ul>

<h3>4) Pools &amp; Water Features (Villas &amp; Facilities)</h3>
<p><strong>Daily / Weekly</strong></p>
<ul>
  <li>Test &amp; balance pH, chlorine/bromine; record readings</li>
  <li>Skim, vacuum, backwash filters; inspect baskets</li>
  <li>Verify pump pressure and leaks; test safety devices</li>
</ul>
<p><strong>Monthly / Quarterly</strong></p>
<ul>
  <li>Inspect tiles, grouting, expansion joints</li>
  <li>Clean DE/sand filters thoroughly; check media condition</li>
  <li>Audit chemical storage and dosing equipment</li>
</ul>
<p><strong>Annually</strong></p>
<ul>
  <li>Replace filter media as required; pressure-test lines</li>
  <li>Electrical safety check for submersible lights &amp; pumps</li>
</ul>

<h3>5) Fire &amp; Life Safety (Commercial; Villas with systems)</h3>
<p><strong>Monthly</strong></p>
<ul>
  <li>Visual check: extinguishers, signage, evacuation plans</li>
  <li>Test manual call points &amp; sounders (staggered by zone)</li>
</ul>
<p><strong>Quarterly</strong></p>
<ul>
  <li>Function test smoke/heat detectors; clean &amp; recalibrate</li>
  <li>Inspect sprinkler valves/gauges; verify pump auto-start</li>
  <li>Test emergency lighting duration</li>
</ul>
<p><strong>Annually</strong></p>
<ul>
  <li>Full fire pump performance test</li>
  <li>Third-party fire system certification (where applicable)</li>
</ul>

<h3>6) Building Envelope &amp; General</h3>
<p><strong>Monthly</strong></p>
<ul>
  <li>Inspect doors/windows seals; adjust closers &amp; hinges</li>
  <li>Check roof drains/gutters; remove debris (sand builds up fast)</li>
  <li>Touch-up sealants/caulks in wet areas</li>
</ul>
<p><strong>Quarterly</strong></p>
<ul>
  <li>Pressure-wash façades where needed; inspect for hairline cracks</li>
  <li>Lubricate hinges, locks, rollers; replace worn weatherstrips</li>
</ul>
<p><strong>Annually</strong></p>
<ul>
  <li>Recoat exterior wood/metal; check waterproofing membranes</li>
</ul>

<h2>Sample Preventive Maintenance Calendar</h2>
<table>
  <thead><tr><th>Frequency</th><th>Tasks (summary)</th></tr></thead>
  <tbody>
    <tr><td>Weekly</td><td>HVAC filters &amp; drains; pool chemistry; visual safety checks</td></tr>
    <tr><td>Monthly</td><td>Electrical panels (thermals), pumps &amp; tanks, emergency lights, envelope checks</td></tr>
    <tr><td>Quarterly</td><td>Coil deep clean, sensor calibration, fire system testing, filter media audits</td></tr>
    <tr><td>Bi-Annual</td><td>BMS sequence validation, roof &amp; façade program, major pool filter service</td></tr>
    <tr><td>Annual</td><td>Chiller/plant service, water tank clean, fire pump test, full electrical testing</td></tr>
  </tbody>
</table>
<blockquote>Pro tip: Run this through a CMMS (computerized maintenance management system). Auto-generated work orders, photo logs, costs, and asset histories make audits painless.</blockquote>

<h2>KPIs to Keep You Efficient</h2>
<ul>
  <li>Reactive vs Preventive: target ≤ 20% reactive</li>
  <li>HVAC availability: ≥ 99% during occupied hours</li>
  <li>Energy intensity: track kWh/m² vs last year (post-coil clean)</li>
  <li>First-time fix rate: ≥ 85%</li>
  <li>Response/Resolution SLAs: e.g., Critical 1–2h / 6–8h</li>
</ul>

<h2>Villa vs Commercial: What Changes?</h2>
<ul>
  <li><strong>Villas:</strong> comfort, pool care, discreet service windows.</li>
  <li><strong>Commercial:</strong> uptime, after-hours works, tenant coordination, statutory testing, documented audits.</li>
</ul>

<h2>Why Hammer Facility?</h2>
<ul>
  <li>In-house MEP &amp; HVAC team (no finger-pointing between vendors)</li>
  <li>Preventive plans tailored to your asset register</li>
  <li>Discreet, uniformed technicians with digital checklists and photo proof</li>
  <li>Energy-aware maintenance that cuts costs without cutting corners</li>
</ul>

<h2>Ready to stop firefighting and start optimizing?</h2>
<p><strong>Let’s build a preventive plan for your property.</strong> <a href="/contact" class="btn btn-primary">Contact Hammer Facility</a> for a site assessment and a customized maintenance calendar.</p>
""",
    },
    {
        "title": "HVAC & MEP Made Simple: How Proactive Service Cuts Energy Costs by 20%+ in Dubai Properties",
        "tag": "Energy",
        "read_minutes": 7,
        "excerpt": "Proactive HVAC/MEP care that actually lowers bills—filters, coil cleaning, airflow balancing, hydronic delta-T, and BMS optimization.",
        "cover_image_url": "https://images.unsplash.com/photo-1517816428104-797678c7cf0d?w=1600&q=80&auto=format&fit=crop",
        "body": """
<h1>HVAC &amp; MEP Made Simple: How Proactive Service Cuts Energy Costs by 20%+ in Dubai Properties</h1>
<p><em>Meta Description:</em> Proactive <strong>HVAC maintenance in Dubai</strong> and smart <strong>MEP services</strong> can slash energy bills by 20%+. Learn the real tasks—coil cleaning, airflow balancing, and <strong>BMS optimization</strong>—that keep villas and commercial spaces efficient year-round.</p>

<h2>Comfort is good. Efficient comfort is better.</h2>
<p>Dubai’s heat, dust, and humidity put serious pressure on building systems. When HVAC and MEP are treated as “set and forget,” energy bills creep up, uptime dips, and comfort becomes a roulette wheel. The fix? <strong>Proactive service</strong>—measurable actions that keep systems tuned, clean, and perfectly coordinated.</p>
<p>At <strong>Hammer Facility</strong>, we don’t just maintain equipment; we make it <em>perform</em>. Here’s how we routinely help villas and commercial properties save <strong>20%+</strong> on energy—without sacrificing comfort.</p>

<h2>The Big Five: Where the Savings Come From</h2>

<h3>1) Filters, Coils &amp; Airflow: The “Easy Wins”</h3>
<ul>
  <li><strong>Filter cycles:</strong> swap/wash on ΔP (pressure drop) schedule.</li>
  <li><strong>Coil cleaning:</strong> quarterly deep cleans on evaporator + condenser coils.</li>
  <li><strong>Airflow &amp; balancing:</strong> verify fan speeds, static pressure, and VAV settings.</li>
</ul>
<p><em>Result:</em> fans work less, compressors cycle properly, and conditioned air reaches people.</p>

<h3>2) Setpoints, Schedules &amp; Night Setback</h3>
<ul>
  <li>Setpoints: residential 23–24°C; commercial by occupancy.</li>
  <li>Schedules: eliminate after-hours operation; use occupancy-based controls.</li>
  <li>Night setback: relax temp targets at night; pre-cool intelligently.</li>
  <li>Humidity control: tweak reheat and fan speeds for comfort at lower energy.</li>
</ul>
<p><em>Result:</em> fewer runtime hours, flatter load profile.</p>

<h3>3) Refrigerant Health &amp; Compressor Life</h3>
<ul>
  <li>Subcooling/superheat checks; electronic leak detection.</li>
  <li>Oil analysis (chillers); condenser fan staging &amp; VFD tuning.</li>
</ul>

<h3>4) Pumps, Valves &amp; Delta-T (Hydronic Gold)</h3>
<ul>
  <li>Optimize VFD curves; trim impellers where appropriate.</li>
  <li>Increase delta-T to move less water for the same cooling.</li>
  <li>Calibrate valves; maintain strainers and air vents.</li>
</ul>

<h3>5) Ducts, Insulation &amp; Heat Gain</h3>
<ul>
  <li>Seal return leaks; repair damaged insulation on risers/roofs.</li>
  <li>Reduce solar gain: shading, reflective films, or glazing upgrades.</li>
</ul>

<h2>Your Proactive Service Plan (Dubai Edition)</h2>
<h3>Monthly (Baseline Health)</h3>
<ul>
  <li>Filters by ΔP; clear condensate drains.</li>
  <li>Light clean grilles/coils; inspect belts &amp; pulleys.</li>
  <li>Check thermostat/BMS setpoints &amp; schedules.</li>
  <li>Visual electrical checks on DBs; test emergency lights (commercial).</li>
</ul>

<h3>Quarterly (Performance Boost)</h3>
<ul>
  <li>Deep-clean coils; re-balance airflows/VAVs.</li>
  <li>Sensor calibration (temp/humidity/CO₂).</li>
  <li>Refrigerant performance checks; leak scan.</li>
  <li>Tune VFDs (fans/pumps); verify sequences.</li>
</ul>

<h3>Annually (Reset &amp; Verify)</h3>
<ul>
  <li>Overhaul AHUs/FCUs (bearings, dampers, seals).</li>
  <li>Hydronic: flush strainers, check delta-T, calibrate valves.</li>
  <li>BMS: clean alarms, remove overrides, optimize schedules.</li>
  <li>Envelope: insulation &amp; glazing review; rooftop plant inspection.</li>
</ul>
<blockquote>Tip: Log everything in a CMMS—work orders, photos, readings, and parts. It’s your truth source for budgets and audits.</blockquote>

<h2>KPIs That Prove It’s Working</h2>
<ul>
  <li>Energy kWh/m² vs last year (normalized).</li>
  <li>Reactive vs Preventive: ≤20% reactive.</li>
  <li>HVAC availability: ≥99% during occupied hours.</li>
  <li>First-time fix rate: ≥85%.</li>
  <li>Complaint volume: should trend down after quarter one.</li>
</ul>

<h2>Villas vs Commercial: What’s Different?</h2>
<ul>
  <li><strong>Villas:</strong> comfort-first, quiet operation, pool &amp; water-heater loads, discreet windows.</li>
  <li><strong>Commercial:</strong> uptime, after-hours works, chiller plants, SLA reporting, compliance.</li>
</ul>

<h2>Ready to turn kWh into savings?</h2>
<p><strong>Start with a site energy walk-through and a fast-win action list (coils, setpoints, schedules, delta-T).</strong> <a href="/contact" class="btn btn-primary">Contact Hammer Facility</a> to book your assessment.</p>
""",
    },
    {
        "title": "Pool Care in Dubai: A Year-Round Guide to Crystal-Clear Water, Compliance & Safety",
        "tag": "Pools",
        "read_minutes": 7,
        "excerpt": "Dubai-specific pool care: chemistry targets, DE/sand filters, safety/compliance, and energy-smart operation for villas and facilities.",
        "cover_image_url": "https://images.unsplash.com/photo-1506126613408-eca07ce68773?w=1600&q=80&auto=format&fit=crop",
        "body": """
<h1>Pool Care in Dubai: A Year-Round Guide to Crystal-Clear Water, Compliance &amp; Safety</h1>
<p><em>Meta Description:</em> Keep your pool sparkling in Dubai’s heat and dust. This <strong>year-round pool maintenance guide</strong> covers chemistry, DE/sand filters, safety, and compliance—so villas and facilities stay crystal clear and guest-ready all year.</p>

<h2>Why Dubai Pools Need a Different Playbook</h2>
<p>Between high heat, sandstorms, and hard water, Dubai pools demand proactive care. With the right schedule and a few smart upgrades, you’ll cut chemicals, reduce downtime, and keep water hotel-grade.</p>

<h2>The Gold Standards (Targets You Should Hit)</h2>
<ul>
  <li><strong>pH:</strong> 7.2–7.6</li>
  <li><strong>Free Chlorine:</strong> 1–3 ppm (residential), 2–4 ppm (heavy use)</li>
  <li><strong>Total Alkalinity:</strong> 80–120 ppm</li>
  <li><strong>Calcium Hardness:</strong> 200–400 ppm</li>
  <li><strong>Cyanuric Acid:</strong> 30–50 ppm</li>
  <li><strong>Salt (SWG):</strong> per OEM (≈ 3,000–3,500 ppm)</li>
</ul>
<blockquote>Pro tip: Log every reading. Trends tell you what a single test can’t.</blockquote>

<h2>Your Year-Round Pool Schedule (Dubai Edition)</h2>
<h3>Weekly (non-negotiables)</h3>
<ul>
  <li>Test &amp; balance pH, chlorine, alkalinity; adjust same day</li>
  <li>Skim, brush, vacuum; clean skimmer and pump baskets</li>
  <li>Top up water to mid-skimmer; check for visible leaks</li>
  <li>Quick visual: tiles, grout, coping, handrails, lights</li>
</ul>

<h3>After Sandstorms</h3>
<ul>
  <li>Shock to 10 ppm free chlorine; brush entire pool; run pump 24–48h</li>
  <li>Backwash filter; clean baskets twice in first 24h</li>
</ul>

<h3>Fortnightly</h3>
<ul>
  <li>Backwash sand/DE filter when pressure rises 8–10 psi from clean baseline</li>
  <li>Clean cartridge (if used); hose from inside out</li>
</ul>

<h3>Monthly</h3>
<ul>
  <li>DE grids: remove &amp; hose clean; recharge with new DE powder</li>
  <li>Inspect seals &amp; unions; lube O-rings; check air relief valves</li>
  <li>Check calcium hardness and CYA; top-up as required</li>
</ul>

<h3>Quarterly</h3>
<ul>
  <li>Deep tile clean (scale line removal)</li>
  <li>Inspect lights &amp; cables; verify RCD/GFCI operation</li>
  <li>Audit chemical storage: lids tight, ventilation clear, labels intact</li>
</ul>

<h3>Pre-Summer (Apr/May)</h3>
<ul>
  <li>Service pump &amp; motor (bearings/noise, shaft seal)</li>
  <li>Check heater/chiller operation; clean condenser coils</li>
  <li>Confirm auto-fill &amp; overflow working (evaporation spikes)</li>
</ul>

<h3>Post-Season (Oct/Nov)</h3>
<ul>
  <li>Lower run-times; review chemical usage; service solar cover/rollers</li>
  <li>Full filter media audit</li>
</ul>

<h2>Filter Mastery: Sand vs DE vs Cartridge</h2>
<h3>Sand Filters</h3>
<ul>
  <li>Backwash at +8–10 psi; rinse 20–30 seconds</li>
  <li>Replace media every 3–5 years (Dubai dust accelerates wear)</li>
  <li>Use clarifier sparingly; overuse can gum the sand</li>
</ul>

<h3>DE (Diatomaceous Earth) Filters</h3>
<ul>
  <li>Best for polish-level clarity</li>
  <li>After backwash, recharge with correct DE dose via skimmer</li>
  <li>Quarterly grid clean; inspect for tears/pinholes</li>
</ul>

<h3>Cartridge Filters</h3>
<ul>
  <li>Rinse monthly; deep clean quarterly</li>
  <li>Replace cartridges every 1–2 years depending on bather load</li>
</ul>
<p><em>Plant-room cheat sheet:</em> keep a laminated card with clean baseline PSI, backwash trigger PSI, and last media change date.</p>

<h2>Safety &amp; Compliance Essentials</h2>
<ul>
  <li>Anti-vortex drain covers, secured and in-date; dual drains or SVRS where required</li>
  <li>Electrical safety: RCD/GFCI protection on all pool circuits; annual test</li>
  <li>Villas: self-closing, self-latching gates; child-safe hardware</li>
  <li>Commercial: depth markers, “no diving,” emergency contacts</li>
  <li>Water testing logs: digital/hard-copy with date, time, readings, actions</li>
  <li>Chemical storage: ventilated, segregate acids from chlorine; PPE on site</li>
</ul>
<p><em>Note:</em> Some commercial pools require periodic third-party water-quality verification. Keep logs audit-ready.</p>

<h2>Chemistry Playbook (Faster Fixes)</h2>
<ul>
  <li><strong>High pH &gt; 7.6:</strong> add muriatic acid gradually; re-test in 30 mins</li>
  <li><strong>Low pH &lt; 7.2:</strong> add soda ash</li>
  <li><strong>Low chlorine + strong sun:</strong> verify CYA 30–50 ppm; consider SWG</li>
  <li><strong>Cloudy water:</strong> check filter PSI; backwash/clean; floc if needed, then vacuum to waste</li>
  <li><strong>Scale on tiles:</strong> lower pH to 7.2–7.3; use descaler; review calcium &amp; TA</li>
  <li><strong>Algae bloom:</strong> shock, brush daily; maintain high FC until overnight loss &lt; 1 ppm</li>
</ul>

<h2>Energy-Smart Pool Ops</h2>
<ul>
  <li>Variable-speed pump (VSP): longer runtimes at lower RPM = clarity with fewer kWh</li>
  <li>Schedule runtimes off-peak; increase after storms/parties</li>
  <li>LED lighting (80–90% less energy)</li>
  <li>Solar cover: reduces evaporation and chemical loss</li>
  <li>Chiller/heater: clean coils; verify setpoints before peak season</li>
</ul>

<h2>Why Hammer Facility?</h2>
<ul>
  <li>In-house pool technicians trained for Dubai conditions</li>
  <li>Plant-room audits with clear PSI baselines &amp; service tags</li>
  <li>Digital logs: chemistry, photos, corrective actions</li>
  <li>One vendor for pool + MEP + HVAC—fewer delays, faster fixes</li>
</ul>

<h2>Ready for resort-grade clarity—every month of the year?</h2>
<p><strong>Let’s set up a year-round pool plan</strong> (chemistry + filtration + safety + energy). <a href="/contact" class="btn btn-primary">Contact Hammer Facility</a> for a site visit and a customized schedule.</p>
""",
    },
    {
        "title": "From Chaos to Control: Why CMMS + Single-Vendor Facility Management Outperforms Ad-Hoc Repairs",
        "tag": "Operations",
        "read_minutes": 7,
        "excerpt": "How CMMS + one accountable vendor delivers reliability, SLAs, real reporting, and fewer call-outs—outperforming ad-hoc maintenance.",
        "cover_image_url": "https://images.unsplash.com/photo-1485827404703-89b55fcc595e?w=1600&q=80&auto=format&fit=crop",
        "body": """
<h1>From Chaos to Control: Why CMMS + Single-Vendor Facility Management Outperforms Ad-Hoc Repairs</h1>
<p><em>Meta Description:</em> Discover why partnering with a <strong>facility management company in Dubai</strong> using a <strong>CMMS</strong> and clear <strong>SLAs</strong> beats ad-hoc repairs. Fewer call-outs, better reporting, lower lifecycle costs. Hammer Facility delivers <strong>turnkey facility services</strong> with one accountable team.</p>

<h2>The Problem with “Fix It When It Breaks”</h2>
<p>Ad-hoc maintenance feels flexible—until it isn’t. You get late-night emergencies, duplicate visits, rising energy bills, missing paperwork, and zero asset history. Costs spike, tenants complain, and nobody can explain where the money went.</p>
<p><strong>The cure:</strong> a <strong>single-vendor FM partner</strong> running a <strong>CMMS (Computerized Maintenance Management System)</strong> and <strong>SLA-backed</strong> workflows. One team, one system, one source of truth.</p>

<h2>What “CMMS + Single Vendor” Actually Means</h2>
<ul>
  <li><strong>Single vendor:</strong> All trades—HVAC, MEP, electrical, plumbing, pools, life-safety—handled by one in-house team.</li>
  <li><strong>CMMS:</strong> Central platform for asset register, work orders, schedules, checklists, photos, spares, SLA timers, and reports.</li>
  <li><strong>SLA framework:</strong> Defined response/resolution times by priority (Critical/High/Normal), with escalation and reporting.</li>
</ul>
<blockquote>Control isn’t a feeling—it’s a workflow.</blockquote>

<h2>Why It Outperforms Ad-Hoc (The Big Wins)</h2>
<h3>1) Reliability &amp; Uptime</h3>
<p>Preventive schedules (filters, coils, pumps, valves) cut failures before they happen. Critical systems hit <strong>≥99% availability</strong> during occupied hours.</p>

<h3>2) Fewer Call-Outs, Faster Fixes</h3>
<p>Technicians arrive with the asset history, last photos, and parts list. First-time fix rates rise; repeat visits drop.</p>

<h3>3) Real Reporting, Real Savings</h3>
<p>Energy, call-outs, spares, and technician time roll up into <strong>monthly dashboards</strong>. You finally see what’s working—and what isn’t.</p>

<h3>4) One Accountable Team</h3>
<p>No vendor parade. Hammer Facility’s in-house MEP &amp; HVAC technicians use unified standards, tools, and QA. Ownership is clear.</p>

<h3>5) Compliance Without the Panic</h3>
<p>Fire/life-safety tests, water-tank cleaning, generator runs—everything is scheduled, logged, and <strong>audit-ready</strong>.</p>

<h2>What a Good SLA Looks Like (Dubai Edition)</h2>
<ul>
  <li><strong>Priority P1 (Critical):</strong> Response ≤ 1–2h, resolution ≤ 6–8h</li>
  <li><strong>Priority P2 (High):</strong> Response ≤ 4h, resolution ≤ 24h</li>
  <li><strong>Priority P3 (Normal):</strong> Response same day, resolution ≤ 72h</li>
</ul>
<p><strong>Included:</strong> photo proof, root-cause notes, parts used, and sign-off in CMMS.<br>
<strong>Escalation:</strong> automatic alerts to supervisor → FM lead → client rep if thresholds are at risk.</p>

<h2>CMMS: The Engine Room</h2>
<ul>
  <li><strong>Asset Register:</strong> make/model/SN, install date, warranty, spares → lifecycle planning.</li>
  <li><strong>PM Schedules:</strong> coils quarterly, tank cleaning annually, fire pump tests monthly → zero lapses.</li>
  <li><strong>Work Orders:</strong> priority, SLA timers, tech notes, photos, signatures → accountability.</li>
  <li><strong>Inventory &amp; Spares:</strong> minimum stock, auto-reorder → faster first-time fixes.</li>
  <li><strong>Energy &amp; KPIs:</strong> kWh/m², ΔP across filters, chiller delta-T, complaint volumes → continuous improvement.</li>
  <li><strong>Reports:</strong> monthly/quarterly PDFs with trends, exceptions, and recommendations → board-ready.</li>
</ul>

<h2>KPI Scorecard (What Great Looks Like)</h2>
<ul>
  <li>Reactive vs Preventive: ≤ 20% reactive</li>
  <li>First-Time Fix Rate: ≥ 85%</li>
  <li>SLA Compliance: ≥ 95% jobs on time</li>
  <li>HVAC Availability: ≥ 99% occupied hours</li>
  <li>Energy Intensity: kWh/m² trending down</li>
  <li>Complaint Volume: falling after Q1</li>
</ul>

<h2>Sample Workflow (From Ticket to Sign-Off)</h2>
<ol>
  <li>Issue logged (tenant portal / QR tag / hotline)</li>
  <li>CMMS classifies priority; SLA timer starts</li>
  <li>Tech dispatched with history, photos, checklists</li>
  <li>On-site fix + before/after photos; parts recorded</li>
  <li>Client sign-off in app; SLA closed</li>
  <li>Report auto-updates dashboards &amp; monthly summaries</li>
</ol>
<blockquote>Every step leaves a breadcrumb. No ghosts, no guesses.</blockquote>

<h2>Cost: The Myth vs The Math</h2>
<p>Ad-hoc feels cheaper—until you count: emergency call-out premiums, duplicate diagnostics, energy waste (dirty coils, bad setpoints), and early equipment failure. <strong>CMMS + single vendor</strong> lowers <em>lifecycle cost</em> via preventive care, faster fixes, and energy optimization (BMS tuning, coil cleaning, delta-T).</p>

<h2>Implementation Roadmap (Fast &amp; Painless)</h2>
<ul>
  <li><strong>Week 1–2:</strong> Asset survey &amp; data capture, priority matrix, SLA agreement</li>
  <li><strong>Week 3–4:</strong> PM schedules loaded to CMMS; quick wins (filters, coil deep clean, schedule tune)</li>
  <li><strong>Month 2–3:</strong> KPI baseline set; energy and complaints drop</li>
  <li><strong>Quarterly:</strong> Review &amp; optimize: add assets, refine checklists, update spares, tune BMS</li>
</ul>

<h2>Villa vs Commercial: What Changes?</h2>
<ul>
  <li><strong>Villas:</strong> discreet service windows, pool plant included, simplified dashboards</li>
  <li><strong>Commercial:</strong> after-hours work, multi-tenant coordination, formal compliance reports, expanded SLA scope</li>
</ul>

<h2>Why Hammer Facility</h2>
<ul>
  <li>Single-vendor, in-house technicians across HVAC, MEP, pools, and life-safety</li>
  <li>CMMS-first operations with photo logs, SLA timers, and board-ready reporting</li>
  <li>Energy-aware maintenance that targets measurable savings</li>
  <li>Dubai-ready playbooks aligned to local conditions and compliance</li>
</ul>

<h2>Ready to move from firefighting to foresight?</h2>
<p><strong>Let’s set up a CMMS demo and map your SLA framework in 30 minutes.</strong> <a href="/contact" class="btn btn-primary">Contact Hammer Facility</a> to put your property on a controlled, data-driven maintenance plan.</p>
""",
    },
]


def seed_insights(service_slug: str = "facility", reset: bool = False) -> None:
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
        if not was_created:
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
        else:
            created += 1

    total = Insight.objects.filter(service=svc).count()
    print(f"✓ Seeded/updated {created} insights for '{service_slug}'. Total now: {total}.")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Seed Hammer Facility insights for a service")
    parser.add_argument("--service", default="facility", help="Service slug")
    parser.add_argument("--reset", action="store_true", help="Delete existing insights before seeding")
    args = parser.parse_args()

    seed_insights(args.service, args.reset)

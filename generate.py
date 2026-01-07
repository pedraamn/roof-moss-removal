#!/usr/bin/env python3

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import csv
import html
import re
import shutil



from dataclasses import dataclass
from pathlib import Path
from datetime import date

@dataclass(frozen=True)
class SiteConfig:
  # Data
  cities_csv: Path = Path("cities.csv")

  def load_cities(self):
    return load_cities_from_csv(self.cities_csv)

  # Brand / site identity
  base_name: str = "Roof Moss Removal"
  brand_name: str = "Roof Moss Removal Company"
  cta_text: str = "Get Free Estimate"
  cta_href: str = "mailto:hello@example.com?subject=Free%20Quote%20Request"

  # Build / assets
  output_dir: Path = Path("public")
  image_filename: str = "picture.png"  # sits next to generate.py

  # Pricing (base range; city pages may apply multipliers)
  cost_low: int = 250
  cost_high: int = 900

  # Page H1 titles
  h1_title: str = "Roof Moss Removal/Moss Cleaning/Roof Moss Treatment Services"
  h1_short: str = "Roof Moss Removal Services"
  h1_sub: str = "Safe moss removal and treatment to protect your roof and prevent long-term damage."

  cost_title: str = "Roof Moss Removal Cost"
  cost_sub: str = "Typical pricing ranges, cost factors, and when professional removal is worth it."

  howto_title: str = "How to Remove Roof Moss"
  howto_sub: str = "What homeowners should know before attempting moss removal on their roof."

  # MAIN PAGE (shared guide)
  main_h2: list[str] = (
    "What Is Roof Moss Removal?",
    "Why Does Moss Grow on Roofs?",
    "Is Roof Moss Bad for Your Roof?",
    "What Types of Roofs Get Moss?",
    "How Fast Does Roof Moss Spread?",
    "Should Roof Moss Be Removed?",
    "When to Hire a Professional for Roof Moss Removal",
  )

  main_p: list[str] = (
    "Roof moss removal is the process of safely removing moss growth from roofing materials to prevent moisture damage and deterioration. Moss holds water against the roof surface, which can shorten the lifespan of shingles and other roofing materials.",
    "Moss grows on roofs because of moisture, shade, and organic debris. North-facing roof slopes, tree-covered areas, and damp climates create ideal conditions for moss to take hold and spread.",
    "Yes, roof moss is bad for your roof because it traps moisture and can lift or separate shingles over time. Left untreated, moss growth increases the risk of leaks, rot, and premature roof failure.",
    "Roof moss commonly grows on asphalt shingles, wood shakes, tile roofs, and composite roofing materials. Any roof that retains moisture or lacks sunlight is more likely to develop moss.",
    "Roof moss can spread quickly once established, especially in damp or shaded conditions. What starts as a small patch can expand across large sections of the roof if not addressed early.",
    "Roof moss should be removed as soon as it’s noticed to prevent long-term damage. Early removal helps protect shingles, improve drainage, and reduce the likelihood of costly roof repairs.",
    "Hiring a professional is recommended when moss covers large areas, when the roof is steep, or when improper removal could damage shingles. Professional roof moss removal reduces safety risks and helps protect the roof surface.",
  )

  # HOW-TO PAGE
  howto_h2: list[str] = (
    "How to Remove Roof Moss",
    "Can You Remove Roof Moss Yourself?",
    "What Kills Roof Moss?",
    "Does Pressure Washing Remove Roof Moss?",
    "How to Prevent Moss From Coming Back",
    "When DIY Roof Moss Removal Is Not Recommended",
  )

  howto_p: list[str] = (
    "To remove roof moss, the growth must be loosened and cleared without damaging the roofing material underneath. Improper scraping or washing can remove protective granules and shorten roof life.",
    "You can remove roof moss yourself in small areas, but it requires careful handling and proper safety precautions. Roof access, slip hazards, and shingle damage are common risks with DIY attempts.",
    "Roof moss is typically killed using treatments that stop growth and allow moss to dry out and detach naturally. Applying the wrong products can discolor or damage roofing materials.",
    "Pressure washing can remove roof moss, but it often causes more harm than good by stripping shingle granules and forcing water under roofing materials. Many roof manufacturers discourage pressure washing for this reason.",
    "Preventing roof moss from coming back usually involves improving sunlight exposure, reducing debris buildup, and applying preventive treatments after removal. Without prevention, moss often returns.",
    "DIY roof moss removal is not recommended for steep roofs, widespread moss growth, or fragile roofing materials. In these cases, professional {roof moss removal services} are the safer option.",
  )

  # COST PAGE
  cost_h2: list[str] = (
    "How Much Does Roof Moss Removal Cost?",
    "What Affects Roof Moss Removal Cost?",
    "Is Professional Roof Moss Removal Worth the Cost?",
  )

  cost_p: list[str] = (
    "Roof moss removal typically costs between a few hundred dollars for small areas and higher amounts for extensive growth. Pricing depends on roof size, moss coverage, and access difficulty.",
    "Factors that affect roof moss removal cost include roof pitch, roofing material, amount of moss, safety requirements, and whether preventive treatments are applied after removal.",
    "Professional roof moss removal is worth the cost when safety, roof protection, and long-term prevention are priorities. Professionals use methods designed to remove moss without damaging shingles or voiding warranties.",
  )

  # LOCAL COST (city-locked variant)
  location_cost_h2: str = "How Much Does Roof Moss Removal Cost in {City, State}?"

  location_cost_p: str = (
    "In {City, State}, most roof moss removal projects range from {cost_lo} to {cost_hi}, "
    "depending on roof size, moss coverage, and how difficult the roof is to access safely. "
    "Prices can vary based on local labor rates, roof pitch, and treatment requirements. "
    "For a clearer breakdown of what affects pricing, you can {view our roof moss removal cost guide}."
  )

  # IMAGES
  image_prompt: str = (
    "A realistic outdoor photo of a roofing professional removing moss from an asphalt shingle roof, "
    "wearing safety harness gear and gloves, using a soft brush and moss treatment applicator; "
    "natural daylight, residential home setting, no staged stock-photo look."
  )




CONFIG = SiteConfig()

CityWithCol = tuple[str, str, float]

def load_cities_from_csv(path: Path) -> tuple[CityWithCol, ...]:
  cities: list[CityWithCol] = []

  with path.open(newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)

    required_fields = {"city", "state", "col"}
    if not reader.fieldnames or not required_fields.issubset(reader.fieldnames):
      raise ValueError(
          "CSV must have headers: city,state,col "
          f"(found: {reader.fieldnames})"
      )

    for i, row in enumerate(reader, start=2):  # header is line 1
      city = (row.get("city") or "").strip()
      state = (row.get("state") or "").strip().upper()
      col_raw = (row.get("col") or "").strip()

      if not city or not state or not col_raw:
        raise ValueError(f"Missing city/state/col at CSV line {i}: {row}")

      try:
        col = float(col_raw)
      except ValueError as e:
        raise ValueError(
            f"Invalid col value at CSV line {i}: {col_raw!r}"
        ) from e

      cities.append((city, state, col))

  return tuple(cities)

CITIES: tuple[CityWithCol, ...] = CONFIG.load_cities()



"""
ALSO_MENTIONED = [
    "pest control",
    "spray",
    "spray bottle",
    "dish soap",
    "wasp stings",
    "price",
    "removal",
    "nest",
    "wasp",
]
"""


# -----------------------
# HELPERS
# -----------------------
def esc(s: str) -> str:
    return html.escape(s, quote=True)


def slugify(s: str) -> str:
    s = s.strip().lower()
    s = re.sub(r"&", " and ", s)
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = re.sub(r"-{2,}", "-", s).strip("-")
    return s


def city_state_slug(city: str, state: str) -> str:
    return f"{slugify(city)}-{slugify(state)}"


def clamp_title(title: str, max_chars: int = 70) -> str:
    if len(title) <= max_chars:
        return title
    return title[: max_chars - 1].rstrip() + "…"


def city_title(city: str, state: str) -> str:
    return clamp_title(f"{CONFIG.h1_short} in {city}, {state}", 70)


def write_text(out_path: Path, content: str) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(content, encoding="utf-8")


def reset_output_dir(p: Path) -> None:
    if p.exists():
        shutil.rmtree(p)
    p.mkdir(parents=True, exist_ok=True)


def copy_site_image(*, src_dir: Path, out_dir: Path, filename: str) -> None:
    src = src_dir / filename
    if not src.exists():
        raise FileNotFoundError(f"Missing image next to generate.py: {src}")
    shutil.copyfile(src, out_dir / filename)


# -----------------------
# THEME (pure CSS, minimal, fast)
# Home-services vibe: warmer neutrals + trustworthy green CTA.
# -----------------------
CSS = """
:root{
  --bg:#fafaf9;
  --surface:#ffffff;
  --ink:#111827;
  --muted:#4b5563;
  --line:#e7e5e4;
  --soft:#f5f5f4;

  --cta:#16a34a;
  --cta2:#15803d;

  --max:980px;
  --radius:16px;
  --shadow:0 10px 30px rgba(17,24,39,0.06);
  --shadow2:0 10px 24px rgba(17,24,39,0.08);
}
*{box-sizing:border-box}
html{color-scheme:light}
body{
  margin:0;
  font-family:ui-sans-serif,system-ui,-apple-system,Segoe UI,Roboto,Helvetica,Arial;
  color:var(--ink);
  background:var(--bg);
  line-height:1.6;
}
a{color:inherit}
a:focus{outline:2px solid var(--cta); outline-offset:2px}

.topbar{
  position:sticky;
  top:0;
  z-index:50;
  background:rgba(250,250,249,0.92);
  backdrop-filter:saturate(140%) blur(10px);
  border-bottom:1px solid var(--line);
}
.topbar-inner{
  max-width:var(--max);
  margin:0 auto;
  padding:12px 18px;
  display:flex;
  align-items:center;
  justify-content:space-between;
  gap:14px;
}
.brand{
  font-weight:900;
  letter-spacing:-0.02em;
  text-decoration:none;
}
.nav{
  display:flex;
  align-items:center;
  gap:12px;
  flex-wrap:wrap;
  justify-content:flex-end;
}
.nav a{
  text-decoration:none;
  font-size:13px;
  color:var(--muted);
  padding:7px 10px;
  border-radius:12px;
  border:1px solid transparent;
}
.nav a:hover{
  background:var(--soft);
  border-color:var(--line);
}
.nav a[aria-current="page"]{
  color:var(--ink);
  background:var(--soft);
  border:1px solid var(--line);
}

.btn{
  display:inline-block;
  padding:9px 12px;
  background:var(--cta);
  color:#fff;
  border-radius:12px;
  text-decoration:none;
  font-weight:900;
  font-size:13px;
  border:1px solid rgba(0,0,0,0.04);
  box-shadow:0 8px 18px rgba(22,163,74,0.18);
}
.btn:hover{background:var(--cta2)}
.btn:focus{outline:2px solid var(--cta2); outline-offset:2px}

/* IMPORTANT: nav links apply grey text; ensure CTA stays white in the toolbar */
.nav a.btn{
  color:#fff;
  background:var(--cta);
  border-color:rgba(0,0,0,0.04);
}
.nav a.btn:hover{background:var(--cta2)}
.nav a.btn:focus{outline:2px solid var(--cta2); outline-offset:2px}

header{
  border-bottom:1px solid var(--line);
  background:
    radial-gradient(1200px 380px at 10% -20%, rgba(22,163,74,0.08), transparent 55%),
    radial-gradient(900px 320px at 95% -25%, rgba(17,24,39,0.06), transparent 50%),
    #fbfbfa;
}
.hero{
  max-width:var(--max);
  margin:0 auto;
  padding:34px 18px 24px;
  display:grid;
  gap:10px;
  text-align:left;
}
.hero h1{
  margin:0;
  font-size:30px;
  letter-spacing:-0.03em;
  line-height:1.18;
}
.sub{margin:0; color:var(--muted); max-width:78ch; font-size:14px}

main{
  max-width:var(--max);
  margin:0 auto;
  padding:22px 18px 46px;
}
.card{
  background:var(--surface);
  border:1px solid var(--line);
  border-radius:var(--radius);
  padding:18px;
  box-shadow:var(--shadow);
}
.img{
  margin-top:14px;
  border-radius:14px;
  overflow:hidden;
  border:1px solid var(--line);
  background:var(--soft);
  box-shadow:var(--shadow2);
}
.img img{display:block; width:100%; height:auto}

h2{
  margin:18px 0 8px;
  font-size:16px;
  letter-spacing:-0.01em;
}
p{margin:0 0 10px}
.muted{color:var(--muted); font-size:13px}
hr{border:0; border-top:1px solid var(--line); margin:18px 0}

.city-grid{
  list-style:none;
  padding:0;
  margin:10px 0 0;
  display:grid;
  gap:10px;
  grid-template-columns:repeat(auto-fit,minmax(180px,1fr));
}
.city-grid a{
  display:block;
  text-decoration:none;
  color:var(--ink);
  background:#fff;
  border:1px solid var(--line);
  border-radius:14px;
  padding:12px 12px;
  font-weight:800;
  font-size:14px;
  box-shadow:0 10px 24px rgba(17,24,39,0.05);
}
.city-grid a:hover{
  transform:translateY(-1px);
  box-shadow:0 14px 28px rgba(17,24,39,0.08);
}

.callout{
  margin:16px 0 12px;
  padding:14px 14px;
  border-radius:14px;
  border:1px solid rgba(22,163,74,0.22);
  background:linear-gradient(180deg, rgba(22,163,74,0.08), rgba(22,163,74,0.03));
}
.callout-title{
  display:flex;
  align-items:center;
  gap:10px;
  font-weight:900;
  letter-spacing:-0.01em;
  margin:0 0 6px;
}
.badge{
  display:inline-block;
  padding:3px 10px;
  border-radius:999px;
  background:rgba(22,163,74,0.14);
  border:1px solid rgba(22,163,74,0.22);
  color:var(--ink);
  font-size:12px;
  font-weight:900;
}
.callout p{margin:0; color:var(--muted); font-size:13px}

footer{
  border-top:1px solid var(--line);
  background:#fbfbfa;
}
.footer-inner{
  max-width:var(--max);
  margin:0 auto;
  padding:28px 18px;
  display:grid;
  gap:10px;
  text-align:left;
}
.footer-inner h2{margin:0; font-size:18px}
.footer-links{display:flex; gap:12px; flex-wrap:wrap}
.footer-links a{color:var(--muted); text-decoration:none; font-size:13px; padding:6px 0}
.small{color:var(--muted); font-size:12px; margin-top:8px}

/* -----------------------
   CONTACT PAGE (matches site theme)
----------------------- */
.form-grid{
  margin-top:14px;
  display:grid;
  gap:14px;
  grid-template-columns: 1fr 320px;
  align-items:start;
}
@media (max-width: 900px){
  .form-grid{grid-template-columns:1fr}
}

.form-card{
  border:1px solid var(--line);
  border-radius:14px;
  padding:14px;
  background:var(--soft);
}

.form{
  display:grid;
  gap:12px;
}
.field label{
  display:block;
  font-size:13px;
  font-weight:800;
  color:var(--ink);
  margin:0 0 6px;
}
.req{color:#ef4444; margin-left:3px}
.input, .textarea{
  width:100%;
  border:1px solid var(--line);
  border-radius:12px;
  padding:10px 12px;
  font:inherit;
  background:#fff;
}
.textarea{min-height:110px; resize:vertical}
.input:focus, .textarea:focus{
  outline:2px solid rgba(22,163,74,0.35);
  outline-offset:2px;
}

.row-2{
  display:grid;
  gap:12px;
  grid-template-columns: 1fr 1fr;
}
@media (max-width: 540px){
  .row-2{grid-template-columns:1fr}
}

.btn-orange{
  display:inline-block;
  width:100%;
  padding:11px 12px;
  border-radius:12px;
  border:1px solid rgba(0,0,0,0.04);
  font-weight:900;
  font-size:13px;
  cursor:pointer;
  background:#d97706;
  color:#fff;
  box-shadow:0 8px 18px rgba(217,119,6,0.18);
}
.btn-orange:hover{background:#b45309}
.btn-orange:focus{outline:2px solid #b45309; outline-offset:2px}

.privacy{
  margin-top:10px;
  text-align:center;
  color:var(--muted);
  font-size:12px;
}

.why-box{
  background:#fff;
  border:1px solid var(--line);
  border-radius:14px;
  padding:14px;
  box-shadow:0 10px 24px rgba(17,24,39,0.05);
}
.why-box h3{
  margin:0 0 10px;
  font-size:15px;
  letter-spacing:-0.01em;
}
.why-list{
  margin:0;
  padding:0;
  list-style:none;
  display:grid;
  gap:10px;
}
.why-item{
  display:flex;
  gap:10px;
  align-items:flex-start;
  color:var(--muted);
  font-size:13px;
}
.tick{
  width:18px;
  height:18px;
  border-radius:999px;
  background:rgba(22,163,74,0.12);
  border:1px solid rgba(22,163,74,0.22);
  display:inline-flex;
  align-items:center;
  justify-content:center;
  flex:0 0 auto;
  margin-top:1px;
}
.tick:before{content:"✓"; font-weight:900; color:var(--ink); font-size:12px; line-height:1}
""".strip()


# -----------------------
# HTML BUILDING BLOCKS
# -----------------------
def nav_html(current: str) -> str:
    def item(href: str, label: str, key: str) -> str:
        cur = ' aria-current="page"' if current == key else ""
        return f'<a href="{esc(href)}"{cur}>{esc(label)}</a>'

    return (
        '<nav class="nav" aria-label="Primary navigation">'
        + item("/", "Home", "home")
        + item("/cost/", "Cost", "cost")
        + item("/how-to/", "How-To", "howto")
        + item("/contact/", "Contact", "contact")
        + f'<a class="btn" href="{esc(CONFIG.cta_href)}">{esc(CONFIG.cta_text)}</a>'
        + "</nav>"
    )


def base_html(*, title: str, canonical_path: str, current_nav: str, body: str) -> str:
    # title == h1 is enforced by callers; keep this thin.
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{esc(title)}</title>
  <link rel="canonical" href="{esc(canonical_path)}" />
  <style>
{CSS}
  </style>
</head>
<body>
  <div class="topbar">
    <div class="topbar-inner">
      <a class="brand" href="/">{esc(CONFIG.brand_name)}</a>
      {nav_html(current_nav)}
    </div>
  </div>
{body}
</body>
</html>
"""


def header_block(*, h1: str, sub: str) -> str:
    return f"""
<header>
  <div class="hero">
    <h1>{esc(h1)}</h1>
    <p class="sub">{esc(sub)}</p>
  </div>
</header>
""".rstrip()

def contact_header_block(*, h1: str, sub: str) -> str:
    return f"""
<header class="contact-hero">
  <div class="hero">
    <h1>{esc(h1)}</h1>
    <p class="sub">{esc(sub)}</p>
  </div>
</header>
""".rstrip()


def footer_block() -> str:
    return f"""
<footer>
  <div class="footer-inner">
    <h2>Next steps</h2>
    <p class="sub">Ready to move forward? Request a free quote.</p>
    <div>
      <a class="btn" href="{esc(CONFIG.cta_href)}">{esc(CONFIG.cta_text)}</a>
    </div>
    <div class="footer-links">
      <a href="/">Home</a>
      <a href="/cost/">Cost</a>
      <a href="/how-to/">How-To</a>
    </div>
    <div class="small">© {esc(CONFIG.brand_name)}. All rights reserved.</div>
  </div>
</footer>
""".rstrip()


def page_shell(*, h1: str, sub: str, inner_html: str, show_image: bool = True) -> str:
    img_src = f"/{CONFIG.image_filename}"
    img_html = ""
    if show_image:
        img_html = f"""
    <div class="img">
      <img src="{esc(img_src)}" alt="Service image" loading="lazy" />
    </div>
""".rstrip()

    return (
        header_block(h1=h1, sub=sub)
        + f"""
<main>
  <section class="card">
{img_html}
    {inner_html}
  </section>
</main>
"""
        + footer_block()
    ).rstrip()



# -----------------------
# CONTENT SECTIONS
# -----------------------

def linkify_curly(text: str) -> str:
  """
  Replace {word} with a link to the homepage using that word as link text
  """
  parts = []
  last = 0

  for m in re.finditer(r"\{([^}]+)\}", text):
    # text before the match
    parts.append(esc(text[last:m.start()]))

    word = m.group(1)
    parts.append(f'<a href="/">{esc(word)}</a>')

    last = m.end()

  # remaining text
  parts.append(esc(text[last:]))

  return "".join(parts)

def make_section(*, headings: list[str], paras:  list[str]) -> str:
  parts = []
  for h2, p in zip(headings, paras):
    parts.append(f"<h2>{esc(h2)}</h2>")
    parts.append(f"<p>{linkify_curly(p)}</p>")
  return "\n".join(parts)

def location_cost_section(city: str, state: str, col: float) -> str:
    cost_lo = f"${int(CONFIG.cost_low * col)}"
    cost_hi = f"${int(CONFIG.cost_high * col)}"

    h2 = CONFIG.location_cost_h2.replace(
        "{City, State}", f"{city}, {state}"
    )

    p = (
        CONFIG.location_cost_p
        .replace("{City, State}", f"{city}, {state}")
        .replace("{cost_lo}", cost_lo)
        .replace("{cost_hi}", cost_hi)
    )

    return f"<h2>{esc(h2)}</h2>\n<p>{esc(p)}</p>"


def city_cost_callout_html(city: str, state: str) -> str:
    # Subtle, high-impact conversion element for city pages.
    return f"""
<div class="callout" role="note" aria-label="Typical cost range">
  <div class="callout-title">
    <span class="badge">Typical range in {esc(city)}, {esc(state)}</span>
    <span>${CONFIG.cost_low}–${CONFIG.cost_high}</span>
  </div>
</div>
""".rstrip()


# -----------------------
# PAGE FACTORY
# -----------------------
def make_page(*, h1: str, canonical: str, nav_key: str, sub: str, inner: str, show_image: bool = True) -> str:
    h1 = clamp_title(h1, 70)
    title = h1  # enforce title == h1
    return base_html(
        title=title,
        canonical_path=canonical,
        current_nav=nav_key,
        body=page_shell(h1=h1, sub=sub, inner_html=inner, show_image=show_image),
    )


def homepage_html() -> str:
    city_links = "\n".join(
        f'<li><a href="{esc("/" + city_state_slug(city, state) + "/")}">{esc(city)}, {esc(state)}</a></li>'
        for city, state, _ in CITIES
    )
    inner = (
        make_section(headings=CONFIG.main_h2, paras=CONFIG.main_p)
        + """
<hr />
<h2>Choose your city</h2>
<p class="muted">We provide services nationwide, including in the following cities:</p>
<ul class="city-grid">
"""
        + city_links
        + f"""
</ul>
<hr />
<p class="muted">
  Also available: <a href="/cost/">{esc(CONFIG.cost_title)}</a> and <a href="/how-to/">{esc(CONFIG.howto_title)}</a>.
</p>
"""
    )

    return make_page(
        h1=CONFIG.h1_title,
        canonical="/",
        nav_key="home",
        sub=CONFIG.h1_sub,
        inner=inner,
    )

def contact_page_html() -> str:
    # Hard-coded copy (per your request)
    h1 = "Get Your Free Estimate"
    sub = "Fill out the form below and we'll connect you with a qualified local professional."

    why_title = "Why Choose Us?"
    why_bullets = (
        "Free, no-obligation estimates",
        "Trusted, experienced professionals",
        "Nationwide service coverage",
        "Fast response times",
    )

    why_items = "\n".join(
        f'<li class="why-item"><span class="tick" aria-hidden="true"></span><span>{esc(t)}</span></li>'
        for t in why_bullets
    )

    inner = f"""
<div class="callout">
  <div class="callout-title">
    <span class="badge">Fast quotes</span>
    <span>Most requests get a response within 1 business day.</span>
  </div>
  <p>Share a few details and we’ll route you to a qualified local pro.</p>
</div>

<div class="form-grid">
  <div class="form-card">
    <form class="form" action="{esc(CONFIG.cta_href)}" method="post">
      <div class="field">
        <label for="full_name">Full Name<span class="req">*</span></label>
        <input class="input" id="full_name" name="full_name" autocomplete="name" placeholder="John Smith" required />
      </div>

      <div class="row-2">
        <div class="field">
          <label for="phone">Phone Number<span class="req">*</span></label>
          <input class="input" id="phone" name="phone" autocomplete="tel" placeholder="(555) 123-4567" required />
        </div>
        <div class="field">
          <label for="zip">ZIP Code<span class="req">*</span></label>
          <input class="input" id="zip" name="zip" autocomplete="postal-code" inputmode="numeric" placeholder="12345" required />
        </div>
      </div>

      <div class="field">
        <label for="email">Email Address<span class="req">*</span></label>
        <input class="input" id="email" name="email" type="email" autocomplete="email" placeholder="john@example.com" required />
      </div>

      <div class="field">
        <label for="details">Project Details</label>
        <textarea class="textarea" id="details" name="details" placeholder="Tell us about your project..."></textarea>
      </div>

      <button class="btn-orange" type="submit">Submit Request</button>

      <div class="privacy">
        By submitting, you agree to be contacted about your project. We respect your privacy.
      </div>
    </form>
  </div>

  <aside class="why-box" aria-label="Why choose us">
    <h3>{esc(why_title)}</h3>
    <ul class="why-list">
      {why_items}
    </ul>
  </aside>
</div>
""".strip()

    return make_page(
        h1=h1,
        canonical="/contact/",
        nav_key="contact",
        sub=sub,
        inner=inner,
        show_image=False
    )


def city_page_html(city: str, state: str, col: float) -> str:
    inner = (
      location_cost_section(city, state, col)
      + make_section(headings=CONFIG.main_h2, paras=CONFIG.main_p)
    )

    return make_page(
        h1=city_title(city, state),
        canonical=f"/{city_state_slug(city, state)}/",
        nav_key="home",
        sub=CONFIG.h1_sub,
        inner=inner,
    )


def cost_page_html() -> str:
    return make_page(
        h1=CONFIG.cost_title,
        canonical="/cost/",
        nav_key="cost",
        sub=CONFIG.cost_sub,
        inner=make_section(headings=CONFIG.cost_h2, paras=CONFIG.cost_p),
    )


def howto_page_html() -> str:
    return make_page(
        h1=CONFIG.howto_title,
        canonical="/how-to/",
        nav_key="howto",
        sub=CONFIG.howto_sub,
        inner=make_section(headings=CONFIG.howto_h2, paras=CONFIG.howto_p),
    )


# -----------------------
# ROBOTS + SITEMAP + WRANGLER
# -----------------------
def robots_txt() -> str:
    return "User-agent: *\nAllow: /\nSitemap: /sitemap.xml\n"


def sitemap_xml(urls: list[str]) -> str:
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "".join(f"  <url><loc>{u}</loc></url>\n" for u in urls)
        + "</urlset>\n"
    )

def wrangler_content() -> str:
    name = CONFIG.base_name.lower().replace(" ", "-")
    today = date.today().isoformat()

    return f"""{{
  "name": "{name}",
  "compatibility_date": "{today}",
  "assets": {{
    "directory": "./public"
  }}
}}
"""


# -----------------------
# MAIN
# -----------------------
def main() -> None:
    script_dir = Path(__file__).resolve().parent
    out = CONFIG.output_dir

    reset_output_dir(out)

    # Copy the single shared image into /public/ so all pages can reference "/picture.png".
    copy_site_image(src_dir=script_dir, out_dir=out, filename=CONFIG.image_filename)

    # Core pages
    write_text(out / "index.html", homepage_html())
    write_text(out / "cost" / "index.html", cost_page_html())
    write_text(out / "how-to" / "index.html", howto_page_html())
    write_text(out / "contact" / "index.html", contact_page_html())

    # City pages
    for city, state, col in CITIES:
        write_text(out / city_state_slug(city, state) / "index.html", city_page_html(city, state, col))

    # robots + sitemap + wrangler
    urls = ["/", "/cost/", "/how-to/"] + [f"/{city_state_slug(c, s)}/" for c, s, _ in CITIES]
    write_text(out / "robots.txt", robots_txt())
    write_text(out / "sitemap.xml", sitemap_xml(urls))
    write_text(script_dir / "wrangler.jsonc", wrangler_content())

    print(f"✅ Generated {len(urls)} pages into: {out.resolve()}")


if __name__ == "__main__":
    main()

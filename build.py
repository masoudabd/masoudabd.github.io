#!/usr/bin/env python3
"""Build index.html from content.json + template.html.

Usage:  python build.py
No dependencies beyond the Python standard library.

Every "focus" variant in content.json is rendered into the page; the
default_focus variant is visible and the others carry the `hidden`
attribute. site.js flips visibility when the URL has ?focus=<key>.
"""
import datetime as _dt
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CONTENT = ROOT / "content.json"
TEMPLATE = ROOT / "template.html"
OUTPUT = ROOT / "index.html"

# Inline tags that content.json text fields may use.
_ALLOWED_TAGS = ("em", "strong", "br")


def esc(text):
    """HTML-escape text, then re-enable the small whitelist of inline tags."""
    if text is None:
        return ""
    out = html.escape(str(text), quote=True)
    for tag in _ALLOWED_TAGS:
        out = out.replace(f"&lt;{tag}&gt;", f"<{tag}>").replace(f"&lt;/{tag}&gt;", f"</{tag}>")
    return out


def attr(text):
    """Escape for use inside a double-quoted attribute (no inline tags)."""
    return html.escape(re.sub(r"<[^>]+>", "", str(text or "")), quote=True)


def wrap_variant(key, default_key, inner):
    hidden = "" if key == default_key else " hidden"
    return f'<div class="v" data-variant="{key}"{hidden}>\n{inner}\n</div>'


def render_hero(v):
    return (
        f'      <p class="kicker">{esc(v["kicker"])}</p>\n'
        f'      <h1>{esc(v["headline"])}</h1>\n'
        f'      <p class="lede">{esc(v["lede"])}</p>'
    )


def render_metrics(v):
    items = "\n".join(
        f'      <li><span class="metric-value">{esc(m["value"])}</span>'
        f'<span class="metric-label">{esc(m["label"])}</span></li>'
        for m in v["metrics"]
    )
    return f'    <ul class="metrics" aria-label="Key numbers">\n{items}\n    </ul>'


def render_about(v):
    paras = "\n".join(f'      <p class="{"lead" if i == 0 else ""}">{esc(p)}</p>' for i, p in enumerate(v["summary"]))
    clusters = "\n".join(
        f'        <div class="cluster"><dt>{esc(c["name"])}</dt><dd>{esc(c["items"])}</dd></div>'
        for c in v["expertise"]
    )
    return (
        f"{paras}\n"
        f'      <h3 class="sub">Core technical expertise</h3>\n'
        f'      <dl class="expertise">\n{clusters}\n      </dl>'
    )


def render_work(v):
    cards = []
    for c in v["work"]:
        cls = "card card-flagship" if c.get("flagship") else "card"
        bullets = ""
        if c.get("bullets"):
            lis = "\n".join(f"          <li>{esc(b)}</li>" for b in c["bullets"])
            bullets = f'\n        <ul class="bullets">\n{lis}\n        </ul>'
        cards.append(
            f'      <article class="{cls}">\n'
            f'        <p class="tag">{esc(c["tag"])}</p>\n'
            f'        <h3>{esc(c["title"])}</h3>\n'
            f'        <p>{esc(c["text"])}</p>{bullets}\n'
            f"      </article>"
        )
    return '    <div class="cards">\n' + "\n".join(cards) + "\n    </div>"


def render_pubs(v, pubs):
    items = []
    for key in v["publications"]:
        p = pubs[key]
        doi_url = f"https://doi.org/{p['doi']}"
        items.append(
            f'      <li>\n'
            f'        <span class="pub-authors">{esc(p["authors"])} ({esc(p["year"])}).</span>\n'
            f'        <a class="pub-title" href="{attr(doi_url)}" rel="noopener">{esc(p["title"])}</a>\n'
            f'        <span class="pub-venue">{esc(p["venue"])} &middot; <span class="doi">doi:{esc(p["doi"])}</span></span>\n'
            f"      </li>"
        )
    return '    <ol class="pubs">\n' + "\n".join(items) + "\n    </ol>"


def render_roles(roles):
    out = []
    for r in roles:
        out.append(
            f'      <div class="role">\n'
            f'        <div class="role-head"><strong>{esc(r["title"])}</strong> &middot; {esc(r["org"])}</div>\n'
            f'        <div class="role-meta">{esc(r["period"])} &middot; {esc(r["where"])}</div>\n'
            f'        <p>{esc(r["note"])}</p>\n'
            f"      </div>"
        )
    return "\n".join(out)


def render_patents(patents):
    out = []
    for p in patents:
        status_cls = re.sub(r"[^a-z]+", "-", p["status"].lower()).strip("-")
        number = f' <span class="patent-number">{esc(p["number"])}</span>' if p.get("number") else ""
        title = esc(p["title"])
        if p.get("url"):
            title = f'<a href="{attr(p["url"])}" rel="noopener">{title}</a>'
        out.append(
            f'      <li>\n'
            f'        <div class="patent-status"><span class="badge badge-{status_cls}">{esc(p["status"])}</span>{number} <span class="patent-date">{esc(p["date"])}</span></div>\n'
            f'        <div class="patent-title">{title}</div>\n'
            f'        <div class="patent-meta">{esc(p["inventors"])} &middot; {esc(p["note"])}</div>\n'
            f"      </li>"
        )
    return "\n".join(out)


def render_education(edu):
    out = []
    for e in edu:
        note = f'\n        <p class="edu-note">{esc(e["note"])}</p>' if e.get("note") else ""
        out.append(
            f'      <div class="edu-row">\n'
            f'        <div class="edu-main"><strong>{esc(e["degree"])}</strong><span class="edu-school">{esc(e["school"])}</span></div>\n'
            f'        <div class="edu-period">{esc(e["period"])}</div>{note}\n'
            f"      </div>"
        )
    return "\n".join(out)


def render_honors(honors):
    return "\n".join(
        f'        <li><span class="honor-year">{esc(h["year"])}</span><span>{esc(h["text"])}</span></li>' for h in honors
    )


def build():
    data = json.loads(CONTENT.read_text(encoding="utf-8"))
    site, stats, variants = data["site"], data["stats"], data["variants"]
    default_key = data["default_focus"]
    if default_key not in variants:
        raise SystemExit(f"default_focus '{default_key}' is not a key of variants {list(variants)}")
    dv = variants[default_key]
    now = _dt.date.today()

    hero = "\n".join(wrap_variant(k, default_key, render_hero(v)) for k, v in variants.items())
    metrics = "\n".join(wrap_variant(k, default_key, render_metrics(v)) for k, v in variants.items())
    about = "\n".join(wrap_variant(k, default_key, render_about(v)) for k, v in variants.items())
    work = "\n".join(wrap_variant(k, default_key, render_work(v)) for k, v in variants.items())
    pubs = "\n".join(wrap_variant(k, default_key, render_pubs(v, data["publications"])) for k, v in variants.items())

    variants_meta = {
        k: {"label": v["label"], "title": v["title"], "description": v["description"], "resume": v["resume"]}
        for k, v in variants.items()
    }

    jsonld = {
        "@context": "https://schema.org",
        "@type": "Person",
        "name": site["name"],
        "honorificSuffix": "Ph.D.",
        "jobTitle": data["roles"][0]["title"],
        "url": site["url"],
        "image": site["url"] + "assets/portrait-640.jpg",
        "email": "mailto:" + site["email"],
        "sameAs": [site["linkedin"], site["scholar"]],
        "worksFor": [{"@type": "Organization", "name": r["org"]} for r in data["roles"]],
        "alumniOf": [{"@type": "CollegeOrUniversity", "name": e["school"]} for e in data["education"]],
        "knowsAbout": [
            "Machine learning", "Deep learning", "Wearable sensors", "Time-series analysis",
            "Signal processing", "Computer vision", "Generative AI", "Vision-language models",
            "Clinical AI", "Human motion analysis",
        ],
    }

    honor_text = site.get("hero_honor") or data["honors"][0]["text"]
    ctx = {
        "default_focus": default_key,
        "variant_keys": ",".join(variants.keys()),
        "title": attr(dv["title"]),
        "og_title": attr(site["name_full"] + " · " + dv["label"]),
        "description": attr(dv["description"]),
        "url": attr(site["url"]),
        "repo": attr(site["repo"]),
        "og_image": attr(site["og_image"]),
        "name_full": attr(site["name_full"]),
        "email": attr(site["email"]),
        "linkedin": attr(site["linkedin"]),
        "scholar": attr(site["scholar"]),
        "location": esc(site["location"]),
        "resume": attr(dv["resume"]),
        "hero_honor": esc(honor_text),
        "hero_variants": hero,
        "metrics_variants": metrics,
        "about_variants": about,
        "work_variants": work,
        "pub_variants": pubs,
        "pub_stats": esc(
            f"{stats['publications']} peer-reviewed publications · {stats['citations']} citations · h-index {stats['h_index']}"
        ),
        "roles": render_roles(data["roles"]),
        "patents": render_patents(data["patents"]),
        "education": render_education(data["education"]),
        "honors": render_honors(data["honors"]),
        "service": esc(data["service"]),
        "variants_meta": json.dumps(variants_meta, ensure_ascii=False).replace("</", "<\\/"),
        "jsonld": json.dumps(jsonld, ensure_ascii=False, indent=2).replace("</", "<\\/"),
        "build_stamp": now.strftime("%Y%m%d"),
        "year": str(now.year),
        "updated": now.strftime("%B %Y"),
    }

    tpl = TEMPLATE.read_text(encoding="utf-8")
    missing = set(re.findall(r"{{(\w+)}}", tpl)) - set(ctx)
    if missing:
        raise SystemExit(f"template references unknown placeholders: {sorted(missing)}")
    out = re.sub(r"{{(\w+)}}", lambda m: ctx[m.group(1)], tpl)
    OUTPUT.write_text(out, encoding="utf-8", newline="\n")
    print(f"wrote {OUTPUT.name} ({len(out.encode('utf-8')) // 1024} KB), default focus = {default_key}, "
          f"variants = {', '.join(variants)}")


if __name__ == "__main__":
    build()

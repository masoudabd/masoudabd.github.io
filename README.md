# masoudabd.github.io

Personal site of Masoud Abdollahi, Ph.D. Static HTML on GitHub Pages, no framework.

## Files

| File | Role |
|---|---|
| `content.json` | **Single source of truth.** All text, links, publications, patents, and the per-focus variants. |
| `template.html` | Page skeleton with `{{placeholders}}`. |
| `build.py` | `python build.py` renders `content.json` + `template.html` into `index.html`. Standard library only. |
| `index.html` | **Generated.** Do not edit by hand; edit `content.json` and rebuild. |
| `styles.css`, `site.js` | Styling and the focus switcher. |
| `assets/` | Portrait (JPEG + WebP), favicon, Open Graph image, résumé PDFs. |

## Focus modes

The page has several "focus" variants that emphasize different parts of the same profile.
Each variant defines its own hero, summary, expertise clusters, selected-work cards, publication order,
and résumé PDF. All variants are rendered into `index.html`; only one is visible.

| Key | Emphasis | URL |
|---|---|---|
| `wearables` | Wearable & health ML (default) | https://masoudabd.github.io/ |
| `healthcare` | Healthcare AI & generative AI | https://masoudabd.github.io/?focus=healthcare |
| `research` | Research scientist | https://masoudabd.github.io/?focus=research |
| `industrial` | Industrial & automotive AI | https://masoudabd.github.io/?focus=industrial |

- **Tailor a link for one application:** put the matching `?focus=` URL on that résumé or cover letter.
- **Change the default the site opens with:** set `"default_focus"` in `content.json`, run `python build.py`, commit and push.
- **Add a variant:** copy an existing block under `"variants"` in `content.json`, give it a new key, rebuild.

## Editing checklist

1. Edit `content.json` (keep facts consistent with the master profile).
2. `python build.py`
3. Open `index.html` locally (or `python -m http.server`) and check the page and each `?focus=` variant.
4. Commit `content.json` and `index.html` together, then push. GitHub Pages redeploys within a minute.

Résumé PDFs in `assets/resume/` are web versions (phone number omitted); regenerate them from the résumé templates when they change.

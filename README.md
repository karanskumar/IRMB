# IRMB Website — Design Prototype

Design prototype for the **Infinite Revenue & Medical Billing LLC** website overhaul
(Weebly → WordPress). Covers the **Home page** and the **Revenue Cycle Management**
service page, which acts as the template for the remaining three service pages.

**Live preview:** enable GitHub Pages (Settings → Pages → Deploy from branch → `main` / root),
then open `https://<user>.github.io/<repo>/`

---

## Contents

| File | What it is |
|---|---|
| `index.html` | The prototype. Fully self-contained — images inlined as data URLs, no build step, no external assets except Google Fonts. Nav links are live: click a Services item to jump to the RCM page. |
| `src-template.html` | Source template with `{{LOGO}}` / `{{LOGO_WHITE}}` / `{{PROFIT}}` placeholders. **Edit this**, not `index.html`. |
| `src/build.py` | Inlines the brand assets into `src-template.html` and writes `index.html`. |
| `src/assets.json` | Pre-encoded logo variants (base64). |
| `src/assets/` | Original brand assets from the client. |

## Rebuilding after an edit

```bash
# edit src-template.html, then:
cd src && python3 build.py       # writes ../index.html
```

Requires `pillow` (`pip install pillow`).

---

## Design tokens

| Token | Value |
|---|---|
| Ink | `#16110F` |
| Crimson | `#96161A` *(sampled from the logo)* |
| Crimson dark | `#7A1115` |
| Crimson tint | `#F7EBEB` |
| Cream | `#FAF7F4` |
| Muted | `#6B605B` |
| Line | `#ECE4DE` |

**Type:** Plus Jakarta Sans (headings) + Inter (body) — both free in Kadence's Google Fonts picker.
**Radius:** 18px cards / 999px buttons. **Rhythm:** 104px desktop, 76px mobile.

All colour pairs meet WCAG 2.1 AA. Crimson on white is 8.7:1.

---

## Notes

- This is a **static prototype for design signoff only** — it is not the WordPress build.
  Every section is deliberately constrained to what free **Kadence + Kadence Blocks** can reproduce.
- Content is drafted from the client's own brand questionnaire answers and the agreed sitemap.
  Anything not yet supplied by the client is tracked separately — do not treat this
  copy as approved.
- `.nojekyll` is present so GitHub Pages serves the files as-is.

## Status

- [x] Home page
- [x] Revenue Cycle Management service page
- [ ] Medical Billing & Coding
- [ ] Credentialing & Contracting
- [ ] Patient Liaison & Advocacy
- [ ] Specialties · About · Testimonials · Contact

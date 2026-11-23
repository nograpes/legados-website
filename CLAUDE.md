# Legados website — project notes for Claude

Bilingual (French/English) static website for **Legados**, a non-profit Spanish
language school and Latin American cultural institute in Montreal's Mile-End
(5804 boul. Saint-Laurent). Replaces the WordPress site at legados.ca, which needed a
paid developer for every change. Aman Verma (repo owner, nograpes) set it up; changes
are requested in chat and made by Claude. Same setup as the CAMI Education site
(nograpes/cami-website). Started 2026-11-23.

## How it works
- `content/fr/*.yml` and `content/en/*.yml` — one file per page per language. A page
  and its translation share the same `key` (the file name). `slug` is the address:
  French pages keep the **same URLs as the old WordPress site** (e.g.
  `cours-d-espagnol-montreal/4-5ans/`) so links and Google results keep working;
  English pages live under `/en/` (e.g. `/en/spanish-classes/4-5-years/`).
- Each page is a list of `sections`. Section types (templates/sections.html):
  `page_title`, `hero_home`, `text` (optional image left/right, `box`, `columns: 2`),
  `facts`, `gallery`, `cards`, `people`, `quote`, `video` (YouTube id), `band`
  (big photo + title), `banner`, `map`. `color` = background
  (white, grey, yellow, orange, red, blue, green, pink, cream, slate).
- Text fields are Markdown. Links to other pages: `page:<key>` or `page:<key>#anchor`
  (in buttons and in Markdown links) — resolved to the same-language page by build.py.
  Use `|` block scalars for text with colons (YAML).
- `content/settings.yml` — menu, footer, contact details, per language.
- `templates/` (Jinja2), `static/` (CSS/JS/fonts/images), `build.py` → `_site/`.
  Preview: `python build.py && python -m http.server 8000 --directory _site`.
  `python build.py --strict` fails on links to unknown pages.
- Images: `/images/YYYY/MM/file` = `static/images/YYYY/MM/file`, same paths as
  WordPress uploads. `import_images.py` (run by the deploy Action) downloads any
  referenced image that's missing from legados.ca/wp-content/uploads and commits it —
  only works while WordPress is online. Always `git pull` after a push.
- `.pages.yml` — Pages CMS editing screens (both page collections). settings.yml is
  deliberately not in Pages CMS (it could drop fields not in its schema).
- `.github/workflows/deploy.yml` — on push to `main` or manually: imports images,
  builds, FTP-uploads `_site/` to Koumbit. Upload is skipped until the secrets
  FTP_SERVER/FTP_USERNAME/FTP_PASSWORD exist (vars FTP_SERVER_DIR, FTP_PROTOCOL optional).

## Design
- Own CSS (static/css/style.css), written from scratch — **don't copy code or layouts
  from the WordPress theme (Astra/Spectra)**; Aman asked for a redesign "in a similar
  style" with no copyright issues. Reused only Legados's own assets: logo, the
  armadillo mascot (Quirquincho), photos, text, Multiblocs.svg, brand colours.
- Fonts self-hosted (no Google Fonts): Ubuntu (Ubuntu Font Licence) for headings,
  Mulish (OFL) for text, from @fontsource; licence files in static/fonts.
- Palette: yellow #efdd17, orange #f6931e, red #ec1c24, button red-orange #ea3b0e,
  blue #00a1ed, green #00aa4e, pink #f6c5dc, footer cream #f4efea.

## Still pointing at the old WordPress site (to replace before WordPress goes away)
- Registration buttons ("Inscription") → WooCommerce shop pages legados.ca/shop/…
- Culture sub-pages (soirée pyjama, Mois de l'héritage latino-américain + MLHA 2026
  program, atelier de poésie), adult private/intensive classes, placement test.
- Newsletter: was Mailchimp (MC4WP plugin). Set `newsletter_action` in settings.yml to
  Mailchimp's embedded-form URL to show the sign-up form; until then the footer shows
  the email address.

## Content questions noticed during migration
- Notre histoire says the project started in 2015; team bios say Mariana founded
  Legados in 2017.
- Andrea Restrepo has no photo on the old site.

"""Build the Legados website.

Reads the editable content in content/ (the files Pages CMS edits), fills in the
templates in templates/, and writes the finished website to _site/.

- French pages:  content/fr/*.yml  ->  _site/<slug>/index.html   (French is the main language)
- English pages: content/en/*.yml  ->  _site/en/<slug>/index.html
- A French page and its English translation share the same `key`.
- Links to other pages can be written `page:<key>` (or `page:<key>#anchor`), in
  buttons and in text; they point to the page in the same language.

Run:  python build.py
Needs: pip install -r requirements.txt
"""
import hashlib
import re
import shutil
import sys
from pathlib import Path

import markdown as md
import yaml
from jinja2 import Environment, FileSystemLoader
from markupsafe import Markup

ROOT = Path(__file__).parent
OUT = ROOT / "_site"
LANGS = ["fr", "en"]
LANG_PREFIX = {"fr": "/", "en": "/en/"}


def load(path):
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def page_url(page, lang):
    slug = (page.get("slug") or "").strip("/")
    return LANG_PREFIX[lang] + (slug + "/" if slug else "")


def relative_links(html, dest):
    """Make site-internal links (/css/…, /images/…, /en/…) relative to the page, so the
    site works both at a domain's root and in a subfolder (e.g. aman.koumbit.org/legados/)."""
    depth = len(dest.relative_to(OUT).parts) - 1
    prefix = "../" * depth or "./"

    def fix(m):
        path = m.group(2)[1:]  # drop the leading /
        return f"{m.group(1)}{prefix}{path}"

    # href="/x", src="/x", url('/x') — but not protocol-relative //host
    return re.sub(r"""((?:href|src)=["']|url\(['"]?)(/(?!/)[^"')]*)""", fix, html)


def main():
    settings = load(ROOT / "content" / "settings.yml")

    pages = {lang: {} for lang in LANGS}
    for lang in LANGS:
        for f in sorted((ROOT / "content" / lang).glob("*.yml")):
            p = load(f)
            p.setdefault("key", f.stem)
            p["_file"] = f"content/{lang}/{f.name}"
            if p.get("published") is False:
                continue
            pages[lang][p["key"]] = p

    problems = []

    def resolve(target, lang, where):
        """Turn 'page:key#anchor' into the page's address in this language."""
        if not target or not isinstance(target, str) or not target.startswith("page:"):
            return target
        key, _, anchor = target[5:].partition("#")
        p = pages[lang].get(key) or pages["fr"].get(key)
        if not p:
            problems.append(f"{where}: link to unknown page '{key}'")
            return "#"
        return page_url(p, lang if key in pages[lang] else "fr") + (f"#{anchor}" if anchor else "")

    if OUT.exists():
        shutil.rmtree(OUT)
    shutil.copytree(ROOT / "static", OUT)

    def fingerprint(rel):
        return hashlib.sha1((OUT / rel).read_bytes()).hexdigest()[:10]

    asset_version = {"css": fingerprint("css/style.css"), "js": fingerprint("js/site.js")}

    env = Environment(loader=FileSystemLoader(ROOT / "templates"), autoescape=True,
                      trim_blocks=True, lstrip_blocks=True)

    current = {"lang": "fr", "where": ""}  # the page being rendered

    def link(target):
        return resolve(target, current["lang"], current["where"])

    def text(value):
        """Markdown -> HTML, with page: links resolved."""
        if not value:
            return ""
        html = md.markdown(str(value), extensions=["extra", "sane_lists", "nl2br"])
        html = re.sub(r'href="(page:[^"]+)"', lambda m: f'href="{link(m.group(1))}"', html)
        return Markup(html)

    def inline(value):
        """Markdown for one short item (no surrounding <p>)."""
        html = str(text(value)).strip()
        return Markup(re.sub(r"^<p>(.*)</p>$", r"\1", html, flags=re.S))

    env.globals.update(link=link, text=text, inline=inline)

    for lang in LANGS:
        s = {**settings.get("common", {}), **settings.get(lang, {})}
        other = "en" if lang == "fr" else "fr"
        for key, page in pages[lang].items():
            current.update(lang=lang, where=page["_file"])
            translation = pages[other].get(key)
            other_url = page_url(translation, other) if translation else LANG_PREFIX[other]
            html = env.get_template("page.html").render(
                page=page, s=s, lang=lang, other_lang=other, other_url=other_url,
                url=page_url(page, lang), v=asset_version, current_key=key,
                menu_keys=lambda item: [item.get("page")] + [c.get("page") for c in item.get("children", [])],
            )
            dest = OUT / page_url(page, lang).lstrip("/") / "index.html"
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(relative_links(html, dest), encoding="utf-8")
        if lang != "fr":
            for key in sorted(set(pages["fr"]) - set(pages[lang])):
                print(f"note: page '{key}' has no {lang} version yet (the language button goes to the {lang} home page)")

    for p in problems:
        print("WARNING:", p)
    print(f"Built {sum(len(v) for v in pages.values())} pages into {OUT}")
    if problems and "--strict" in sys.argv:
        sys.exit(1)


if __name__ == "__main__":
    main()

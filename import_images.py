"""Copy the images the site uses from the old WordPress site into static/images/.

Content refers to images as /images/2026/04/photo.webp. If static/images/2026/04/photo.webp
is missing, this downloads https://legados.ca/wp-content/uploads/2026/04/photo.webp.
Run by the GitHub Action before each build (it commits whatever it downloads), so it only
matters while the WordPress site is still online. Safe to run any number of times.
"""
import re
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).parent
DEST = ROOT / "static" / "images"
SOURCE = "https://legados.ca/wp-content/uploads/"
PATTERN = re.compile(r"/images/(\d{4}/\d{2}/[^\s\"')]+?\.(?:jpe?g|png|webp|svg|gif))", re.I)


def main():
    wanted = set()
    for f in (ROOT / "content").rglob("*.yml"):
        wanted.update(PATTERN.findall(f.read_text(encoding="utf-8")))
    fetched = failed = 0
    for rel in sorted(wanted):
        target = DEST / rel
        if target.exists():
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        try:
            req = urllib.request.Request(SOURCE + rel, headers={"User-Agent": "legados-website-import"})
            with urllib.request.urlopen(req, timeout=60) as r:
                target.write_bytes(r.read())
            fetched += 1
            print("downloaded", rel)
        except Exception as e:  # keep going; report at the end
            failed += 1
            print("FAILED", rel, e, file=sys.stderr)
    print(f"{len(wanted)} images referenced, {fetched} downloaded, {failed} failed")


if __name__ == "__main__":
    main()

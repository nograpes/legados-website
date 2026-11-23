# Legados website

Bilingual (French/English) website for Legados, published to Koumbit.

| Folder / file | What it is |
| --- | --- |
| `content/fr/`, `content/en/` | The text of every page, one file per page and language. |
| `content/settings.yml` | Menu, footer and contact details. |
| `static/` | Stylesheet, script, fonts and images (`static/images/`). |
| `templates/` | Page layouts. Change these only to change the design. |
| `build.py` | Combines content and templates into the finished site in `_site/`. |
| `.pages.yml` | Editing screens for [Pages CMS](https://pagescms.org). |
| `.github/workflows/deploy.yml` | Builds the site and uploads it to Koumbit after every change. |

## Preview locally

```
pip install -r requirements.txt
python build.py
python -m http.server 8000 --directory _site
```

Then open http://localhost:8000 (English: http://localhost:8000/en/).

## Publishing

Every change pushed to `main` is built and uploaded to Koumbit by FTP. The FTP login
goes in the repository's Settings → Secrets and variables → Actions:
secrets `FTP_SERVER`, `FTP_USERNAME`, `FTP_PASSWORD`; optional variables
`FTP_SERVER_DIR` (folder on Koumbit, ending in `/`) and `FTP_PROTOCOL` (`ftps` or `ftp`).

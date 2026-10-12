# my-journey-through-vedanta

Personal study journal built with MkDocs Material and published at https://vedanta.pavanturlapati.com/.
Pages follow the pattern **handwritten note → AI-assisted explanation**, with the photo of the original page at the end.

## Setup

```sh
pip install -r requirements.txt
```

## Preview and build

```sh
mkdocs serve            # live preview at http://127.0.0.1:8000
mkdocs build --strict   # same check CI runs; fails on broken links/config
```

Pushing to `main` deploys to GitHub Pages via `.github/workflows/deploy.yml`.

## Adding a new handwritten page

1. Prepare the photo (resizes, fixes rotation, strips EXIF/location data):

   ```sh
   python tools/add_handwritten_image.py <path-to-photo> <chapter> <YYYY-MM-DD> [page]
   ```

   This writes `docs/assets/handwritten-notes/chapter-NN-YYYY-MM-DD-page-NN.jpg`.
2. Copy `templates/chapter-page-template.md` to `docs/chapter-NN/NN-short-slug.md` and fill it in.
3. Add the page to `nav` in `mkdocs.yml`, to `docs/chapter-NN/index.md`, and to the chapter summary page.
4. Run `mkdocs build --strict`.

## Layout

- `docs/` — site content (`chapter-01/`, `preface/`, `reflections/`, `assets/handwritten-notes/`)
- `templates/` — page template (not published)
- `tools/` — helper scripts
- `overrides/` — theme overrides

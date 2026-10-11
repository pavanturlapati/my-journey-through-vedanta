---
name: festival-series-hub
description: Create or update a festival or multi-day series hub page (such as Navaratri) in the Vedanta MkDocs site. Use when adding a new festival series, publishing a new day or article to an existing hub, or updating the Reflections navigation.
---

# Festival Series Hub

The site is MkDocs Material, in the repo root `my-journey-through-vedanta/`. A series hub is one page under `docs/reflections/` that gives a short intro and then one short blurb and link per article. It is updated in place as articles are published. The Navaratri hub, `docs/reflections/navaratri.md`, is the reference example.

Use `templates/hub-page.md` as the starting point for a new hub.

## Creating a new hub

1. Create `docs/reflections/<festival>.md`. Use a **year-neutral** filename (`navaratri.md`, not `navaratri-2026.md`) so the URL is stable and the page can be reused.
2. Fill in the template: title, "Series started" date, "Progress" and "Last updated" lines, an intro of 2 short paragraphs, then a "Start Here" section and one section per day or part.
3. List **all** planned days up front. Unpublished days show `*Coming soon.*` with no dates, because tithi dates shift each year.
4. Add the page to `mkdocs.yml` under `nav` > Reflections > **Festivals**.
5. Add it to the "Festivals" list in `docs/reflections/index.md`.

## Publishing a new day

1. Replace `*Coming soon.*` under that day with a blurb of **2 lines** and a link. Each blurb should name the deity or theme, the quality she stands for, and one Vedantic angle. Don't open every blurb the same way.
2. Update `Progress` (for example, "Day 2 of 9 published") and `Last updated`.
3. Use descriptive link text, such as `[Read Day 2: Brahmacharini and Discipline →](URL)`, never a bare "Read more".
4. Ask the user for the article URL. Never guess a slug.

## Link rules

- If the article is **not** in this repo, use its full live URL: `https://vedanta.pavanturlapati.com/reflections/<slug>/`.
- If the article **is** in this repo, use a relative `.md` link so `mkdocs build --strict` checks it.
- Each article should link back to the hub with a line such as `Part of the [Navaratri series](/reflections/navaratri/)`. Add it if the article is in this repo. Otherwise remind the user.

## Content rules

- Keep blurbs short, distinct and faithful to the actual article. Ask the user for the article summary if you haven't seen it.
- Don't invent doctrine. Where Vedanta is connected to a tradition, say it is a reading or reflection.
- Don't put dates on unpublished days.

## Navigation structure

Reflections in `mkdocs.yml` are grouped as: Overview, **Festivals** (series hubs), **Personal Questions** (single reflections). Keep `docs/reflections/index.md` in step with the nav.

## Publish checklist

1. Run `mkdocs build --strict` (after `pip install -r requirements.txt`) and fix any warnings.
2. Commit and push to `main`. Pushing to `main` triggers `.github/workflows/deploy.yml`, which builds and deploys to GitHub Pages at https://vedanta.pavanturlapati.com/.
3. Don't commit or push unless the user asks.
4. After the deploy, check the live hub page and its links.

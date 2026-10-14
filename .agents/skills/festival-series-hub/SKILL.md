---
name: festival-series-hub
description: Create or update a festival or multi-day series hub page (such as Navaratri) in the Vedanta MkDocs site. Use when adding a new festival series, publishing a new day or article to an existing hub, or updating the Articles navigation.
---

# Festival Series Hub

The site is MkDocs Material, in the repo root `my-journey-through-vedanta/`. A series hub is one page under `docs/reflections/` that gives a short intro and then one short blurb and link per article. It is updated in place as articles are published. The Navaratri hub, `docs/reflections/navaratri.md`, is the reference example.

Use `templates/hub-page.md` as the starting point for a new hub.

## Creating a new hub

1. Create `docs/reflections/<festival>.md`. Use a **year-neutral** filename (`navaratri.md`, not `navaratri-2026.md`) so the URL is stable and the page can be reused.
2. Fill in the template: title, "Series started" date, "Progress" and "Last updated" lines, an intro of 2 short paragraphs, then a "Start Here" section and one section per day or part.
3. List **all** planned days up front. Unpublished days show `*Coming soon.*` with no dates, because tithi dates shift each year.
4. Add the page to `mkdocs.yml` under `nav` > Articles > **Festivals** (files stay in `docs/reflections/` so URLs don't change).
5. Add it to the "Festivals" list in `docs/articles/index.md` (use `../reflections/...` links).

## Publishing a new day

1. Replace `*Coming soon.*` under that day with a blurb of **2 lines** and a link. Each blurb should name the deity or theme, the quality she stands for, and one Vedantic angle. Don't open every blurb the same way.
2. Add the day to the main-site Journal entry too (see "Journal entry on the main site" below).
3. Update `Progress` (for example, "Day 2 of 9 published") and `Last updated`.
4. Use descriptive link text, such as `[Read Day 2: Brahmacharini and Discipline →](URL)`, never a bare "Read more".
5. Ask the user for the article URL. Never guess a slug.
6. Add the day to the consolidated reflections page (see below).
7. Add the article to `mkdocs.yml` under Articles > Festivals > the series entry, and to the nested list under the series in `docs/articles/index.md` (use `../reflections/...` links). Do **not** add Navaratri pages to `docs/reflections/index.md`, which is only for personal questions.
8. After inserting any nav or list line, check its indentation (`grep -n`), because the edit tool can add extra leading spaces and break the YAML.

## Daily article template

Every day article follows `templates/day-article.md`. Fixed section order: (1) how the day is observed, (2) the story, (3) the form and symbols, (4) everyday example, (5) Vedantic lens, (6) questions and the answer box, (7) the invitation, then the acknowledgement and study disclaimer, with nothing after it.

Rules:

- H1 format: `Day N of Navaratri — <Form>: <question>?`, with the back-link directly under it.
- Exactly 5 questions, all on the day's theme, and 5 generic hints. No side topics. Move them to a later day if needed.
- One credited public image (Wikimedia Commons). Check the file name with `curl -I` and the licence with the Commons API. Use the credit format in the template.
- Verify mantras, scripture quotes and stories before writing. Hedge customs with "commonly" or "in some regions", and don't state unverified offerings or colours as fact.
- Don't state a calendar date. Tithi dates shift.
- Don't add the "reverence and gratitude" line. It was removed on purpose.
- Day 1 was refactored to this template on October 12, 2026. Days 2 to 4 follow it; Day 4 is the latest reference example.

## Link rules

- Articles live in this repo under `docs/reflections/`, so use a **relative `.md` link** (for example `navaratri-day-2-brahmacharini.md`). `mkdocs build --strict` then catches broken links.
- Use a full live URL (`https://vedanta.pavanturlapati.com/reflections/<slug>/`) only for a page that is not in this repo.
- Every article in a series must have `*Part of the [<Series name>](<hub>.md).*` directly under its H1 title. Add it when you add the article. Also add the article to `mkdocs.yml` under the hub's nav entry and to the nested list in `docs/articles/index.md`.

## Content rules

- Keep blurbs short, distinct and faithful to the actual article. Ask the user for the article summary if you haven't seen it.
- Don't invent doctrine. Where Vedanta is connected to a tradition, say it is a reading or reflection.
- Don't put dates on unpublished days.
- Every new page (hub, day article, or any article) must start with front matter containing a one-sentence `description:` of under about 160 characters, placed above the H1. It feeds social share previews and the RSS feed. Format: `Day N of Navaratri: <Form> and <theme>.` for day articles, and a plain summary of the page for hubs. Always wrap the value in double quotes, because a colon inside an unquoted value breaks the YAML and the description is silently ignored. Match the style of existing pages.

## Navigation structure

In `mkdocs.yml`, **Articles** holds Overview, **Temples** and **Festivals** (series hubs and their day articles); **Reflections** holds Overview and **Personal Questions** only. Festival pages stay in `docs/reflections/` so URLs don't change, but they are listed in the nav and in `docs/articles/index.md`, not in `docs/reflections/index.md`.

## Reflection answer boxes (private PDF journal)

Articles that end with a numbered list of reflection questions get answer boxes and a print-to-PDF button. The reader's answers stay in their browser (`localStorage`). Nothing is sent to the site owner, and the page says so.

1. Put the questions in one or more numbered lists. Start each item with a **bold short question**. The script uses the bold text as the heading in the PDF and the rest of the item as its description. To group questions, put a `####` heading directly above a list. Every numbered list between the section's `##` heading and the block is used, in order. Start later lists at the right number (for example `6.`) so the page matches the boxes.
2. Directly after the lists (and any closing sentence), add a line with the key, title and optional hints:

   ```html
   <div class="reflection-journal" data-key="navaratri-day-2" data-title="Day 2 of Navaratri: ..." data-hints="hint 1|hint 2|hint 3"></div>
   ```

   `data-key` must be unique per article. Use the article's series and day. `data-hints` is optional: one short, generic example per question, separated by `|`, in question order. They show as grey "Example:" placeholder text, vanish when the reader types, and are never saved or put in the PDF. Write them generically, not as the author's real answers, and keep them short so they don't lead the reader.
3. Keep a day's questions focused on that day's theme. Put side topics in a clearly labelled second group, or move them to a later day.
4. The script is `docs/javascripts/reflection-journal.js` (loaded through `extra_javascript` in `mkdocs.yml`) and the styling is in `docs/stylesheets/extra.css`. Don't copy either into an article.
5. The block already includes the steps, the "I do not receive your answers" notice and the not-professional-advice disclaimer, and the PDF repeats the disclaimer. Don't weaken or remove that wording.
6. The PDF is a print-friendly page that the reader saves as a PDF. It is not generated by a library, so it works in every script and language.
7. `docs/privacy.md` already mentions the answer boxes. Update it if the behaviour changes.
8. A placeholder-free build won't show the boxes, because they are created in the browser. Check in a browser that the boxes appear and that "Open print-friendly page" works.

## Consolidated reflections page

`docs/reflections/navaratri-all-reflections.md` shows every day's questions and answer box in one place. The individual articles keep their own boxes. For each newly published day:

1. Add a `## Day N: <Form>, <Question>` section **before** the line `*Days X to 9 will be added here as they are published.*` and update that line.
2. Under it: `Read the article: [Day N — <Form>](<article>.md)`, the 5 questions copied **exactly** from the article, then the `reflection-journal` div with the **same `data-key`, `data-title` and `data-hints`** as the article. The same key makes answers sync between the article and this page.
3. Each day must be its own `##` section containing only its own list, because the script collects every `<ol>` back to the previous H1/H2. Use no extra headings or lists between the questions and the div.
4. Keep the acknowledgement and study disclaimer last.

## Journal entry on the main site

Each series also gets one entry in the main site (`pt-site`, a separate repo at `../pt-site`) that routes readers to the Vedanta hub.

1. Create `src/content/journal/<series-slug>.md` in `pt-site`. Frontmatter keys are strict: `title`, `description`, `date`, `tags` and optional `draft`. Use `tags: ["vedanta"]`, because tags must come from `journalTags` in `src/config.ts`.
2. Write 2 short paragraphs about the festival and the series, mention that the articles are AI-assisted study notes, then a "Read the series" list with the **hub link first** and one link per published article. Use full live URLs, since the repos are separate.
3. Link the hub prominently. **Add each newly published day to this entry as part of publishing it** (one line: link plus a short description), in the same pass as the hub update. The user chose this so the Journal page never goes stale. Remember it's a separate repo, so it needs its own build, commit and push, and a `git pull --rebase` may be needed because an automated Letterboxd sync commits to that repo.
4. Run `npm run build` in `pt-site` to check it. Commit and push there separately, only when the user asks. That repo has its own deploy.

## Publish checklist

1. Run `mkdocs build --strict` (after `pip install -r requirements.txt`) and fix any warnings.
1a. Confirm the consolidated page has the new day's section (5 textareas per day).
2. Commit and push to `main`. Pushing to `main` triggers `.github/workflows/deploy.yml`, which builds and deploys to GitHub Pages at https://vedanta.pavanturlapati.com/.
3. Don't commit or push unless the user asks.
4. After the deploy, check the live hub page and its links.

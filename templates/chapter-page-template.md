<!--
TEMPLATE - not published (lives outside docs/).

WORKFLOW when sharing a new handwritten page:
 1. Share the image path (e.g. C:\pt-auto\2026-Q4\images\IMG_xxx.jpeg) plus:
    chapter number, session date/time, and (optionally) a topic title.
 2. Image is processed (resize + strip EXIF) with:
      python tools/add_handwritten_image.py <image> <chapter> <YYYY-MM-DD> [page]
    which writes docs/assets/handwritten-notes/chapter-NN-YYYY-MM-DD-page-NN.jpg
 3. Page is created at docs/chapter-NN/NN-short-slug.md using the next unused
    number. The chapter summary always holds the highest number (currently
    12-summary-and-questions.md). When adding a page:
      a. rename the summary to the next number (e.g. 12 -> 13),
      b. update its links (nav, chapter index) and add a redirect for the old
         URL under plugins > redirects > redirect_maps in mkdocs.yml.
 4. Update: mkdocs.yml nav, docs/chapter-NN/index.md (topic list + session dates),
    and the chapter summary page (new summary paragraph, session list entry
    linking to the page's #original-handwritten-page, and new Q&A numbered in order).
 5. Run `mkdocs build --strict` and fix anything it reports before committing.
 6. AUDIO (after the page is final, because audio is generated from the text):
      python tools/generate_audio.py chapter-NN --dry-run   # shows new/CHANGED pages, no cost
      python tools/publish_audio.py chapter-NN              # generate, rebuild feed, upload
    Only new or edited pages are generated (hash check). The player on each
    page and the podcast feed pick up new chapter folders automatically.
    When the summary page is renumbered (step 3a), delete the old summary MP3
    in ../audio/chapter-NN/ and run upload_audio.py --prune so the bucket and
    feed do not keep a duplicate. Audio is not committed to git; the
    OpenAI key and R2 keys live outside the repo (.env, Windows variables).

BEFORE EDITING: run `git pull --rebase origin main`. The remote has had
edits made outside this workflow; check for an existing version of the page.

RULES
 - Transcribe the handwriting faithfully (fix only spelling); keep quotes,
   numbering and boxed/underlined words (use <strong>).
 - "handwritten-note" div = transcription; "ai-note" div = explanation.
   Inside divs use HTML (<strong>, <em>), not markdown emphasis.
 - Do not add claims beyond the notes in the handwritten-note block.
   AI interpretation and nuance go in ai-note only.
 - Personal reflections get their own "My Reflection - ..." section.
 - Use `??? question "..."` collapsibles (answer indented 4 spaces).
 - Image goes last, under "Original Handwritten Page", clickable.
 - Only the last page of a chapter should say "final"; otherwise say "continuation".
 - Closing/summary text that is not from the handwriting goes inside an ai-note div.
 - Never write literal "\n" in markdown; use real line breaks.
 - Nav entries in mkdocs.yml: keep indentation identical to sibling lines; quote
   titles containing a colon. Chapters live under the collapsible "Vedanta Treatise"
   section (Preface, Chapter 1, Chapter 2, ...); add new chapters there as siblings.
 - Commit message style: short imperative subject, no trailing period.
 - Add front matter at the very top of the page with a one-sentence `description:`
   (used for social share previews and the RSS feed). Without it the generic site
   description is shown when the page is shared.
-->

---
description: "{{ One sentence summary, under about 160 characters. Keep the double quotes: a colon in an unquoted value breaks the YAML. }}"
---

# {{ Page title }}

**Study session:** {{ Month D, YYYY }} — {{ time / weekday }}
**Source:** {{ optional, e.g. Handwritten continuation of *Chapter N — Title* }}

{{ Optional 1-2 sentence intro. }}

## {{ Section heading 1 }}

<div class="handwritten-note">
{{ Faithful transcription of this part of the page. }}
</div>

<div class="ai-note">
{{ Plain-language explanation, nuance, everyday example. Avoid overclaiming. }}
</div>

## {{ Section heading 2 }}

<div class="handwritten-note">
{{ Transcription. }}
</div>

<div class="ai-note">
{{ Explanation. }}
</div>

## My Reflection — {{ question }}

<!-- Only if the notes contain a personal reflection -->

<div class="handwritten-note">
{{ Reflection transcription. }}
</div>

<div class="ai-note">
{{ Gentle response; keep open questions open. }}
</div>

## Reflection to Carry Forward

> **{{ One question to carry forward }}**

## Check Your Understanding

??? question "1. {{ Question }}"
    {{ Answer. }}

??? question "2. {{ Question }}"
    {{ Answer. }}

## Original Handwritten Page

[![Original handwritten notes — {{ Chapter/topic }}, {{ date }}](../assets/handwritten-notes/chapter-NN-YYYY-MM-DD-page-NN.jpg)](../assets/handwritten-notes/chapter-NN-YYYY-MM-DD-page-NN.jpg)

The typed text above follows this page. The photograph can be replaced later with a clearer scan without changing the study text.

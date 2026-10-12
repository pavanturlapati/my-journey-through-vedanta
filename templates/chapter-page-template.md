<!--
TEMPLATE - not published (lives outside docs/).

WORKFLOW when sharing a new handwritten page:
 1. Share the image path (e.g. C:\pt-auto\2026-Q4\images\IMG_xxx.jpeg) plus:
    chapter number, session date/time, and (optionally) a topic title.
 2. Image is processed (resize + strip EXIF) with:
      python tools/add_handwritten_image.py <image> <chapter> <YYYY-MM-DD> [page]
    which writes docs/assets/handwritten-notes/chapter-NN-YYYY-MM-DD-page-NN.jpg
 3. Page is created at docs/chapter-NN/NN-short-slug.md (next unused number;
    the chapter summary is always the highest number, e.g. 12-summary; when adding
        a page, rename the summary to the next number and update its links + the redirect in mkdocs.yml).
 4. Update: mkdocs.yml nav, docs/chapter-NN/index.md (topic list + session dates),
    and docs/chapter-NN/08-summary-and-questions.md (summary paragraph + session list).

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
-->

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

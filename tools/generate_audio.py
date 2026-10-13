"""Generate one MP3 per docs page with OpenAI TTS.

Usage:
    python tools/generate_audio.py chapter-01 --dry-run   # show size, no cost
    python tools/generate_audio.py chapter-01             # generate
    python tools/generate_audio.py preface

Output goes outside the repo, to ../audio/<folder>/NN-slug.mp3. A hash of each
page's spoken text is kept in hashes.json, so re-running only pays for new or
edited pages. Existing MP3s with no hash yet are trusted and recorded.
Delete an MP3 to force regeneration.

Needs OPENAI_API_KEY (see tts_sample.py). Standard library only.
"""

import argparse
import hashlib
import html
import json
import re
import sys
import time
import urllib.error
from pathlib import Path

from tts_sample import get_key, synthesize

MODEL = "gpt-4o-mini-tts"
VOICE = "alloy"
SLOW = 0.1  # the approved "slow10" setting from tts_sample.py
SPEED = round(1 - SLOW, 2)
EXTRA = f" Speak about {round(SLOW * 100)}% slower than your normal pace."
MAX_CHARS = 3500  # API limit is 4096 characters per request

DOCS = Path(__file__).resolve().parents[1] / "docs"
OUT = Path(__file__).resolve().parents[2] / "audio"


def clean(md):
    """Turn a markdown page into plain text suitable for reading aloud."""
    md = re.sub(r"\A---\n.*?\n---\n", "", md, flags=re.S)  # front matter
    md = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", md)  # images
    md = re.sub(r"<!--.*?-->", "", md, flags=re.S)
    md = re.sub(r"\?\?\?\+?\s+\w+\s+\"([^\"]*)\"", r"\1", md)  # ??? question "text"
    md = re.sub(r"^!!!\s+\w+(\s+\"([^\"]*)\")?\s*$", r"\2", md, flags=re.M)
    md = re.sub(r"<[^>]+>", "", md)  # html tags, keep their text
    md = html.unescape(md)
    md = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", md)  # links -> text
    md = re.sub(r"\{[:.#][^}]*\}", "", md)  # attribute lists
    md = re.sub(r"(\*\*|__|\*|_|`)", "", md)  # emphasis, code
    md = re.sub(r"^>\s?", "", md, flags=re.M)  # blockquotes
    md = re.sub(r"^\s*[-*+]\s+", "", md, flags=re.M)  # bullets
    md = re.sub(r"^\s*(\d+)\.\s+", r"\1. ", md, flags=re.M)
    md = re.sub(r"^\s*\|.*\|\s*$", "", md, flags=re.M)  # tables
    md = re.sub(r"^\s*(-{3,}|\*{3,}|_{3,})\s*$", "", md, flags=re.M)  # horizontal rules
    md = re.sub(r"\s*→\s*", ", then ", md)
    md = re.sub(r"\s*—\s*", ", ", md)
    md = md.replace("–", "-")

    lines = []
    for line in md.splitlines():
        m = re.match(r"^#{1,6}\s+(.*)$", line)
        if m:  # headings: end with a full stop so there is a pause
            text = m.group(1).strip()
            line = text if text.endswith((".", "?", "!", ":")) else text + "."
        lines.append(line.strip())
    return re.sub(r"\n{2,}", "\n\n", "\n".join(lines)).strip()


def chunks(text):
    """Split on paragraph (then sentence) boundaries, under MAX_CHARS."""
    pieces = []
    for para in text.split("\n\n"):
        if len(para) <= MAX_CHARS:
            pieces.append(para)
        else:
            pieces.extend(re.split(r"(?<=[.!?])\s+", para))
    out, cur = [], ""
    for p in pieces:
        if cur and len(cur) + len(p) + 2 > MAX_CHARS:
            out.append(cur)
            cur = p
        else:
            cur = f"{cur}\n\n{p}" if cur else p
    if cur:
        out.append(cur)
    return out


def speak(key, text):
    for attempt in range(4):
        try:
            return synthesize(key, MODEL, VOICE, text, SPEED, EXTRA)
        except urllib.error.HTTPError as err:
            if err.code in (429, 500, 502, 503) and attempt < 3:
                time.sleep(2 ** (attempt + 1))
                continue
            raise SystemExit(f"API error {err.code}: {err.read().decode()[:300]}")
        except OSError:
            if attempt < 3:
                time.sleep(2 ** (attempt + 1))
                continue
            raise


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("folder", help="folder under docs/, e.g. chapter-01 or preface")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--index", action="store_true", help="read the folder's index.md instead of its subpages")
    args = parser.parse_args()

    src = DOCS / args.folder
    if args.index:
        pages = [src / "index.md"]
    else:
        pages = sorted(p for p in src.glob("*.md") if p.name != "index.md")
    if not pages:
        sys.exit(f"No pages found in {src}")

    key = None if args.dry_run else get_key()
    if not args.dry_run and not key:
        sys.exit("OPENAI_API_KEY is not set.")

    out_dir = OUT / args.folder
    total = 0
    for page in pages:
        text = clean(page.read_text(encoding="utf-8"))
        total += len(text)
        target = out_dir / ("00-full-preface.mp3" if args.index else page.stem + ".mp3")
        digest = hashlib.sha256((MODEL + VOICE + text).encode()).hexdigest()
        manifest_path = out_dir / "hashes.json"
        manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
        if args.dry_run:
            state = "new" if not target.exists() else ("unchanged" if manifest.get(target.name) == digest else "CHANGED")
            print(f"{page.name}: {len(text)} chars, {len(chunks(text))} chunk(s), {state}")
            continue
        if target.exists() and (manifest.get(target.name) == digest or target.name not in manifest):
            if target.name not in manifest:
                manifest[target.name] = digest
                manifest_path.write_text(json.dumps(manifest, indent=1))
            print(f"skip {target.name} (unchanged)")
            continue
        out_dir.mkdir(parents=True, exist_ok=True)
        data = b"".join(speak(key, c) for c in chunks(text))
        target.write_bytes(data)
        manifest[target.name] = digest
        manifest_path.write_text(json.dumps(manifest, indent=1))
        print(f"saved {target} ({len(data) // 1024} KB)")
    print(f"total spoken text: {total} chars")


if __name__ == "__main__":
    main()

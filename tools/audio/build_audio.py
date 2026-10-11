"""Turn narration scripts in audio-scripts/ into MP3s in docs/audio/ with Kokoro.

Usage (from the repo root, inside .venv-audio):
    python tools/audio/build_audio.py                     # all scripts, skip unchanged
    python tools/audio/build_audio.py preface/index       # one page
    python tools/audio/build_audio.py --voice bm_george --speed 0.9
    python tools/audio/build_audio.py --force

Script format (audio-scripts/<page>.txt):
    - paragraphs separated by blank lines get a short pause between them
    - a line like "[pause 2.5]" inserts that many seconds of silence
    - lines starting with "#" are comments
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from pathlib import Path

os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")

import lameenc
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = ROOT / "audio-scripts"
OUTPUT_DIR = ROOT / "docs" / "audio"
PRONUNCIATIONS = Path(__file__).with_name("pronunciations.json")
MANIFEST = SCRIPTS_DIR / "manifest.json"

SAMPLE_RATE = 24000
PARAGRAPH_PAUSE = 0.6
PAUSE_RE = re.compile(r"^\[pause\s+([0-9.]+)\]$", re.IGNORECASE)


def load_pronunciations() -> dict[str, str]:
    return json.loads(PRONUNCIATIONS.read_text(encoding="utf-8"))


def apply_pronunciations(text: str, table: dict[str, str]) -> str:
    for word, respelling in sorted(table.items(), key=lambda kv: -len(kv[0])):
        text = re.sub(rf"\b{re.escape(word)}\b", respelling, text)
    return text


def clean_for_speech(text: str) -> str:
    text = text.replace("\u2014", ", ").replace("\u2013", ", ")
    text = text.replace("\u2019", "'").replace("\u201c", '"').replace("\u201d", '"')
    return re.sub(r"\s+", " ", text).strip()


def parse_script(raw: str) -> list[tuple[str, str | float]]:
    """Return a list of ("text", paragraph) and ("pause", seconds) items."""
    items: list[tuple[str, str | float]] = []
    paragraph: list[str] = []

    def flush() -> None:
        if paragraph:
            items.append(("text", " ".join(paragraph)))
            paragraph.clear()

    for line in raw.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            continue
        if not stripped:
            flush()
            continue
        match = PAUSE_RE.match(stripped)
        if match:
            flush()
            items.append(("pause", float(match.group(1))))
        else:
            paragraph.append(stripped)
    flush()
    return items


def silence(seconds: float) -> np.ndarray:
    return np.zeros(int(SAMPLE_RATE * seconds), dtype=np.float32)


def encode_mp3(audio: np.ndarray) -> bytes:
    pcm = (np.clip(audio, -1.0, 1.0) * 32767).astype(np.int16)
    encoder = lameenc.Encoder()
    encoder.set_bit_rate(64)
    encoder.set_in_sample_rate(SAMPLE_RATE)
    encoder.set_channels(1)
    encoder.set_quality(2)
    return encoder.encode(pcm.tobytes()) + encoder.flush()


def synthesize(items, pipeline, voice: str, speed: float, table: dict[str, str]) -> np.ndarray:
    chunks: list[np.ndarray] = []
    total = sum(1 for kind, _ in items if kind == "text")
    done = 0
    for kind, value in items:
        if kind == "pause":
            chunks.append(silence(float(value)))
            continue
        done += 1
        text = apply_pronunciations(clean_for_speech(str(value)), table)
        print(f"  [{done}/{total}] {text[:70]}...", flush=True)
        for _, _, audio in pipeline(text, voice=voice, speed=speed):
            chunks.append(np.asarray(audio, dtype=np.float32))
        chunks.append(silence(PARAGRAPH_PAUSE))
    return np.concatenate(chunks)


def fingerprint(raw: str, voice: str, speed: float, table: dict[str, str]) -> str:
    payload = json.dumps([raw, voice, speed, table], sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("pages", nargs="*", help="page ids like preface/index (default: all)")
    parser.add_argument("--voice", default="am_michael", help="Kokoro voice (default: am_michael)")
    parser.add_argument("--speed", type=float, default=0.95, help="speaking speed (default: 0.95)")
    parser.add_argument("--force", action="store_true", help="regenerate even if unchanged")
    args = parser.parse_args()

    if args.pages:
        scripts = [SCRIPTS_DIR / f"{page}.txt" for page in args.pages]
    else:
        scripts = sorted(SCRIPTS_DIR.rglob("*.txt"))

    missing = [s for s in scripts if not s.exists()]
    if missing:
        print("Script not found: " + ", ".join(str(m) for m in missing), file=sys.stderr)
        return 1

    table = load_pronunciations()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8")) if MANIFEST.exists() else {}

    pipeline = None
    for script in scripts:
        page_id = script.relative_to(SCRIPTS_DIR).with_suffix("").as_posix()
        raw = script.read_text(encoding="utf-8")
        digest = fingerprint(raw, args.voice, args.speed, table)
        output = OUTPUT_DIR / f"{page_id}.mp3"

        if not args.force and output.exists() and manifest.get(page_id) == digest:
            print(f"{page_id}: unchanged, skipping")
            continue

        if pipeline is None:
            from kokoro import KPipeline

            print(f"Loading Kokoro (voice={args.voice}, speed={args.speed})...", flush=True)
            pipeline = KPipeline(lang_code=args.voice[0], repo_id="hexgrad/Kokoro-82M")

        print(f"{page_id}: generating", flush=True)
        audio = synthesize(parse_script(raw), pipeline, args.voice, args.speed, table)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(encode_mp3(audio))
        manifest[page_id] = digest
        MANIFEST.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"{page_id}: wrote {output.relative_to(ROOT)} ({len(audio) / SAMPLE_RATE / 60:.1f} min)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

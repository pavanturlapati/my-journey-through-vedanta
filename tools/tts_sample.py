"""Generate short OpenAI TTS samples so you can compare voices by ear.

Usage:
    python tools/tts_sample.py                # default text and voices
    python tools/tts_sample.py --file docs/preface/essence-of-vedanta.md

Needs the OPENAI_API_KEY environment variable. Uses only the standard library.
Samples are written outside the repo, to ../audio-samples/.
"""

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

URL = "https://api.openai.com/v1/audio/speech"

DEFAULT_TEXT = (
    "Vedanta does not ask us to reject the world. It asks us to understand "
    "its nature accurately, so that we do not demand permanent psychological "
    "security from impermanent conditions. The inquiry moves from what "
    "objects exist, toward the basis because of which any experience is "
    "known at all. This is the Atman, the Self, which Vedanta declares to be "
    "Brahman."
)

INSTRUCTIONS = (
    "Accent: a warm, natural Indian English accent, like a learned teacher "
    "from India. Pace: slow and calm, with natural pauses. "
    "Pronounce Sanskrit words such as Vedanta, Atman and Brahman exactly as "
    "an Indian speaker would, with retroflex and dental consonants."
)

# (model, voice) pairs to compare. File names get an -indian suffix.
VARIANTS = [
    ("gpt-4o-mini-tts", "onyx"),
    ("gpt-4o-mini-tts", "echo"),
    ("gpt-4o-mini-tts", "fable"),
    ("gpt-4o-mini-tts", "alloy"),
    ("gpt-4o-mini-tts", "shimmer"),
]


def get_key():
    key = os.environ.get("OPENAI_API_KEY")
    if key or sys.platform != "win32":
        return key
    # Fall back to the saved Windows user variable, for apps started before
    # `setx` ran and so still holding the old environment.
    try:
        import winreg

        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as k:
            return winreg.QueryValueEx(k, "OPENAI_API_KEY")[0]
    except OSError:
        return None


def synthesize(key, model, voice, text, speed=None, extra=""):
    body = {"model": model, "voice": voice, "input": text, "response_format": "mp3"}
    if speed:
        body["speed"] = speed
    if model.startswith("gpt-4o"):
        body["instructions"] = INSTRUCTIONS + extra
    req = urllib.request.Request(
        URL,
        data=json.dumps(body).encode(),
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        return resp.read()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", help="read text from this file instead (first 1200 chars)")
    parser.add_argument("--voice", help="only this voice, instead of all variants")
    parser.add_argument("--slow", type=float, help="slow down by this fraction, e.g. 0.1 for 10%%")
    args = parser.parse_args()

    key = get_key()
    if not key:
        sys.exit("OPENAI_API_KEY is not set. Open a new terminal after running setx.")

    text = DEFAULT_TEXT
    if args.file:
        text = Path(args.file).read_text(encoding="utf-8")[:1200]

    out_dir = Path(__file__).resolve().parents[2] / "audio-samples"
    out_dir.mkdir(exist_ok=True)

    variants = [v for v in VARIANTS if not args.voice or v[1] == args.voice]
    for model, voice in variants:
        jobs = [(f"{model}-{voice}-indian.mp3", None, "")]
        if args.slow:
            pct = round(args.slow * 100)
            jobs.append((
                f"{model}-{voice}-indian-slow{pct}.mp3",
                round(1 - args.slow, 2),
                f" Speak about {pct}% slower than your normal pace.",
            ))
        for fname, speed, extra in jobs:
            name = out_dir / fname
            try:
                name.write_bytes(synthesize(key, model, voice, text, speed, extra))
                print(f"saved {name} ({name.stat().st_size} bytes)")
            except urllib.error.HTTPError as err:
                print(f"{fname} failed: {err.code} {err.read().decode()[:300]}")


if __name__ == "__main__":
    main()

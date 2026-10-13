"""Publish audio for a folder in one step: generate, rebuild feed, upload.

Usage:
    python tools/publish_audio.py chapter-02

Before the first run for a new chapter, add it to SECTIONS in make_feed.py.
Existing MP3s are skipped, so only new pages cost money.
"""

import subprocess
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent


def run(script, *args):
    code = subprocess.run([sys.executable, str(TOOLS / script), *args]).returncode
    if code:
        sys.exit(code)


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    run("generate_audio.py", sys.argv[1])
    run("make_feed.py")
    run("upload_audio.py")


if __name__ == "__main__":
    main()

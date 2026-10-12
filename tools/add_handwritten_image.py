"""Prepare a handwritten-note photo for the site.

Resizes, applies EXIF rotation, strips all metadata (GPS, device) and saves as
docs/assets/handwritten-notes/chapter-NN-YYYY-MM-DD-page-NN.jpg

Usage:
    python tools/add_handwritten_image.py <source-image> <chapter> <YYYY-MM-DD> [page]

Example:
    python tools/add_handwritten_image.py ../images/IMG_1234.jpeg 1 2026-09-02
"""
import sys
from pathlib import Path

from PIL import Image, ImageOps

MAX_WIDTH = 1600
DEST = Path(__file__).resolve().parent.parent / "docs" / "assets" / "handwritten-notes"


def main() -> None:
    if len(sys.argv) < 4:
        sys.exit(__doc__)
    src = Path(sys.argv[1])
    chapter = int(sys.argv[2])
    date = sys.argv[3]
    page = int(sys.argv[4]) if len(sys.argv) > 4 else 1

    out = DEST / f"chapter-{chapter:02d}-{date}-page-{page:02d}.jpg"
    with Image.open(src) as im:
        im = ImageOps.exif_transpose(im).convert("RGB")
        if im.width > MAX_WIDTH:
            im = im.resize((MAX_WIDTH, round(im.height * MAX_WIDTH / im.width)), Image.LANCZOS)
        clean = Image.new("RGB", im.size)
        clean.paste(im)  # fresh image: no EXIF/metadata carried over
        clean.save(out, "JPEG", quality=85, optimize=True, progressive=True)
    print(f"Saved {out} ({out.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()

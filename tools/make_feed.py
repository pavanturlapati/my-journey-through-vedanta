"""Build the podcast feed (audio/feed.xml) from the generated MP3s.

Usage:
    python tools/make_feed.py

Episodes are ordered preface first, then chapter-01, using the page titles
(first # heading) from docs/. Feed type is "serial", so podcast apps play
episodes oldest-first, like an audiobook. After running, upload with
python tools/upload_audio.py.
"""

import re
from datetime import datetime, timedelta, timezone
from email.utils import format_datetime
from pathlib import Path
from xml.sax.saxutils import escape

BASE = "https://audio.pavanturlapati.com"
SITE = "https://vedanta.pavanturlapati.com/"
TITLE = "My Journey Through Vedanta"
DESCRIPTION = (
    "Audio version of the study notes at vedanta.pavanturlapati.com, "
    "inspired by Vedanta Treatise by A. Parthasarathy."
)

ROOT = Path(__file__).resolve().parents[2]
AUDIO = ROOT / "audio"
DOCS = Path(__file__).resolve().parents[1] / "docs"

# Extra sections first, then every chapter-NN folder found under audio/.
SECTIONS = [("preface", "Preface", "preface")] + [
    (p.name, f"Chapter {int(p.name.split('-')[1])}", p.name)
    for p in sorted(AUDIO.glob("chapter-[0-9][0-9]"))
]


def mp3_seconds(path):
    """Estimate duration from the first MPEG frame header (assumes CBR)."""
    data = path.read_bytes()
    bitrates = [0, 32, 40, 48, 56, 64, 80, 96, 112, 128, 160, 192, 224, 256, 320]  # MPEG1 L3
    bitrates2 = [0, 8, 16, 24, 32, 40, 48, 56, 64, 80, 96, 112, 128, 144, 160]  # MPEG2 L3
    i = 0
    if data[:3] == b"ID3":
        i = 10 + ((data[6] << 21) | (data[7] << 14) | (data[8] << 7) | data[9])
    while i < len(data) - 4:
        if data[i] == 0xFF and (data[i + 1] & 0xE0) == 0xE0:
            version = (data[i + 1] >> 3) & 3  # 3 = MPEG1, 2 = MPEG2
            idx = data[i + 2] >> 4
            if version in (2, 3) and 0 < idx < 15:
                table = bitrates if version == 3 else bitrates2
                return len(data) * 8 / (table[idx] * 1000)
        i += 1
    return 0


def hms(seconds):
    s = int(seconds)
    return f"{s // 3600:02d}:{s % 3600 // 60:02d}:{s % 60:02d}"


def page_title(folder, stem, fallback):
    md = DOCS / folder / (stem + ".md")
    if md.is_file():
        for line in md.read_text(encoding="utf-8").splitlines():
            if line.startswith("# "):
                return line[2:].strip()
    return fallback


def main():
    items = []
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    n = 0
    for folder, label, src in SECTIONS:
        files = sorted((AUDIO / folder).glob("*.mp3"))
        for k, f in enumerate(files, 1):
            n += 1
            stem = re.sub(r"^\d+-", "", f.stem)
            title = page_title(src, f.stem, None) or page_title(src, stem, stem.replace("-", " ").title())
            if f.stem == "00-full-preface":
                full = "Preface"
            else:
                full = f"{label}, Part {k}: {title}"
            secs = mp3_seconds(f)
            pub = format_datetime(start + timedelta(hours=n))
            items.append(f"""    <item>
      <title>{escape(full)}</title>
      <description>{escape(full)}. From {escape(TITLE)}.</description>
      <link>{SITE}</link>
      <guid isPermaLink="false">vedanta-{folder}-{f.stem}</guid>
      <pubDate>{pub}</pubDate>
      <enclosure url="{BASE}/{folder}/{f.name}" length="{f.stat().st_size}" type="audio/mpeg"/>
      <itunes:duration>{hms(secs)}</itunes:duration>
      <itunes:episode>{n}</itunes:episode>
      <itunes:explicit>false</itunes:explicit>
    </item>""")

    feed = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd">
  <channel>
    <title>{escape(TITLE)}</title>
    <link>{SITE}</link>
    <language>en-in</language>
    <description>{escape(DESCRIPTION)}</description>
    <itunes:author>Pavan Turlapati</itunes:author>
    <itunes:image href="{BASE}/cover.jpg"/>
    <itunes:type>serial</itunes:type>
    <itunes:explicit>false</itunes:explicit>
    <itunes:category text="Religion &amp; Spirituality"/>
{chr(10).join(items)}
  </channel>
</rss>
"""
    (AUDIO / "feed.xml").write_text(feed, encoding="utf-8")
    print(f"wrote {AUDIO / 'feed.xml'} with {len(items)} episodes")


if __name__ == "__main__":
    main()

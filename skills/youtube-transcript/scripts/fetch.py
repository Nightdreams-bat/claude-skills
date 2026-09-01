#!/usr/bin/env python3
"""Fetch a YouTube video's metadata + transcript using yt-dlp. Stdlib only."""
import argparse
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")


def normalize(url_or_id: str) -> str:
    if re.fullmatch(r"[A-Za-z0-9_-]{11}", url_or_id):
        return f"https://www.youtube.com/watch?v={url_or_id}"
    return url_or_id


def parse_vtt(text: str):
    segments = []
    seen = set()
    for block in text.split("\n\n"):
        lines = [l for l in block.splitlines() if l.strip()]
        if not lines:
            continue
        tstamp = None
        body = []
        for l in lines:
            m = re.match(r"(\d+:\d+:\d+\.\d+)\s+-->", l)
            if m:
                tstamp = m.group(1)
                continue
            if l.startswith("WEBVTT") or l.startswith("Kind:") or l.startswith("Language:"):
                continue
            body.append(re.sub(r"<[^>]+>", "", l).strip())
        line = " ".join(b for b in body if b)
        if line:
            segments.append({"start": tstamp or "", "text": line})
    # YouTube auto-captions roll: each cue repeats the tail of the previous one.
    # Rebuild a clean stream by only appending the non-overlapping suffix.
    cleaned = []
    acc_words = []
    for seg in segments:
        w = seg["text"].split()
        if not w:
            continue
        overlap = 0
        maxk = min(len(w), len(acc_words), 20)
        for k in range(maxk, 0, -1):
            if acc_words[-k:] == w[:k]:
                overlap = k
                break
        new = w[overlap:]
        if not new and w == acc_words[-len(w):]:
            continue
        acc_words.extend(new or w)
        cleaned.append({"start": seg["start"], "text": " ".join(new or w)})
    return cleaned


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("url")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--lang", default="en")
    args = ap.parse_args()

    url = normalize(args.url)

    meta = run(["yt-dlp", "-J", "--no-warnings", "--skip-download", url])
    if meta.returncode != 0:
        print(meta.stderr.strip() or "yt-dlp failed", file=sys.stderr)
        return 1
    info = json.loads(meta.stdout)
    title = info.get("title", "?")
    channel = info.get("channel") or info.get("uploader", "?")
    dur = info.get("duration")
    dur_s = f"{dur // 60}:{dur % 60:02d}" if isinstance(dur, int) else "?"

    with tempfile.TemporaryDirectory() as td:
        out = run([
            "yt-dlp", "--skip-download", "--write-subs", "--write-auto-subs",
            "--sub-langs", f"{args.lang}.*,{args.lang}", "--sub-format", "vtt",
            "--no-warnings", "-o", str(Path(td) / "cap.%(ext)s"), url,
        ])
        vtts = list(Path(td).glob("*.vtt"))
        segments = []
        if vtts:
            segments = parse_vtt(vtts[0].read_text(encoding="utf-8", errors="replace"))

    if args.json:
        json.dump({"title": title, "channel": channel, "duration": dur_s,
                   "url": url, "segments": segments}, sys.stdout, ensure_ascii=False, indent=2)
        print()
        return 0

    print(f"TITLE: {title}")
    print(f"CHANNEL: {channel}")
    print(f"DURATION: {dur_s}")
    print(f"URL: {url}")
    print()
    if not segments:
        print("(no captions available for this video)")
        return 0
    para = " ".join(s["text"] for s in segments)
    for chunk in re.findall(r".{1,600}(?:\s|$)", para):
        print(chunk.strip())
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main())

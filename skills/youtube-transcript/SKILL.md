---
name: youtube-transcript
description: Fetch a YouTube video's title, metadata, and full transcript as text/JSON so it can be summarized, quoted, or turned into a lesson. Use whenever the user gives a YouTube URL or asks what a video says.
---

# YouTube transcript

Ported in spirit from amosblomqvist/pi-config's `youtube-transcript`.

Needs `yt-dlp` on PATH (already installed for this user at
`yt-dlp`).

## Tool

```
python "~/.claude/skills/youtube-transcript/scripts/fetch.py" <url-or-id> [--json] [--lang en]
```

- Prints `TITLE`, `CHANNEL`, `DURATION`, `URL`, then the transcript as plain
  paragraphs (timestamps stripped).
- `--json` emits `{title, channel, duration, url, segments:[{start,text}]}`.
- `--lang` picks the caption language; falls back to auto-generated captions.

## How to use

1. Run the script with the URL.
2. If it errors with "no captions", tell the user the video has no transcript
   available — do not try to transcribe audio yourself.
3. Then do whatever the user asked: summarize, extract steps, or (if they want
   to learn the content) hand off to the `teach` skill using the transcript as
   the source.

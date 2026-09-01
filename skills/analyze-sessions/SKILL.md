---
name: analyze-sessions
description: Analyze past Claude Code sessions on this machine — token/cost rollups, most-used tools, prompt-pattern mining, and rendering an old session to readable text. Use when the user asks "how much have I spent", "what do I use Claude for", "show me that session from yesterday", or wants usage stats.
---

# Analyze sessions

Claude Code stores every session as JSONL under `~/.claude/projects/<slug>/<session-id>.jsonl`.
This skill reads those files locally. Nothing leaves the machine.

Ported in spirit from amosblomqvist/pi-config's `analyze-sessions`.

## Tool

`scripts/analyze.py` (stdlib only, needs Python 3).

```
python "~/.claude/skills/analyze-sessions/scripts/analyze.py" <command> [args]
```

Commands:

| Command | What it does |
|---|---|
| `cost [--days N] [--project SLUG]` | Token totals and estimated USD, grouped by day and by model. |
| `tools [--days N]` | Count of each tool call across sessions, most used first. |
| `prompts [--days N] [--top N]` | Your user prompts, first line only, most recent first — for spotting what you repeatedly ask. |
| `sessions [--days N]` | One row per session: date, project, #turns, tokens, est. cost. |
| `render <session-id-or-path>` | Print a session as plain readable text (user / assistant / tool calls). |

Cost numbers are **estimates** from a built-in price table (Sonnet/Opus/Haiku);
treat them as directional, not billing-accurate.

## How to use

1. Run the command that matches the question.
2. Summarize the output for the user — don't just paste the table if it's long.
3. For `render`, if the user only gave a vague reference ("yesterday's freight repo session"),
   first run `sessions --days 3` to find the id, then `render` it.

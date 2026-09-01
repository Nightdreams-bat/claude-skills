---
name: web-debug
description: Playbook for debugging a frontend / web app with the Chrome browser tools — reproduce a bug, read console errors and network failures, inspect the DOM, and verify a fix in the live page. Use when the user reports something broken on a website or local dev server.
---

# Web debug

Ported in spirit from amosblomqvist/pi-config's `web-debug`.

Claude Code drives a real Chrome tab through the `mcp__claude-in-chrome__*`
tools. This skill is the order of operations — not new tools.

## Setup

1. `tabs_context_mcp` — see the user's existing tabs. Never reuse an old tab id.
2. `tabs_create_mcp` — open a fresh tab for the debugging work.
3. `navigate` to the failing URL (localhost dev server or live site).

## The loop

1. **Reproduce.** Do the exact steps the user described (`computer` for
   clicks/typing/scrolling, `form_input` for form fields, `find` to locate an
   element). Confirm you see the same broken behavior.
2. **Read the evidence** — before theorizing:
   - `read_console_messages` (use `pattern:` to filter, e.g. the app name or
     `error`) — JS exceptions, failed assertions, warnings.
   - `read_network_requests` — non-2xx responses, CORS failures, wrong payloads,
     slow calls.
   - `read_page` / `get_page_text` — what the DOM actually contains vs expected.
   - `javascript_tool` — evaluate expressions in page context to check state
     (component props, global vars, computed styles). Never trigger `alert`,
     `confirm`, or `prompt` — they freeze the tab.
3. **Form one hypothesis.** State it to the user: "X is failing because Y."
4. **Fix** in the source (outside the browser).
5. **Verify.** Reload the tab, re-run the reproduction, confirm console/network
   are clean and the behavior is correct.
6. If you want the user to see the fix, `gif_creator` a short before/after.

## Guardrails

- Stop and ask the user after 2–3 failed tool attempts, a dialog freeze, or if
  the page won't load — don't keep retrying or wander to unrelated pages.
- Don't click "Delete" / "Pay" / destructive buttons to reproduce unless the
  user explicitly said to; warn first.

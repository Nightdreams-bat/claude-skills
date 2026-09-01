# Claude Code config audit rubric

Every check traces to a principle the user has learned (Obsidian `StudyVault/Claude Code`)
or to the official CLAUDE.md quality criteria. Cite the principle in each finding — the
report teaches *why*, it does not just hand out chores.

## Grading (per area)

| Grade | Meaning |
|-------|---------|
| **A** | no findings, or trivial-only |
| **B** | LOW findings only |
| **C** | at least one MED finding |
| **F** | at least one HIGH finding |

**Overall tier = the worst area's grade.** State it, and name which area dragged it down.
Goal state is A everywhere.

Severity: **HIGH** = wasting credits or corrupting output every session · **MED** = drift
that will bite soon · **LOW** = polish.

---

## TOP-PRIORITY TRANSFORM — CLAUDE.md / always-loaded → index

If `~/.claude/CLAUDE.md`, `memory/MEMORY.md`, or any always-injected file is oversized
(A1/A2 below) **or** holds situational detail inline (A4), the remediation plan's **#1
item, always**, is: *convert it to an index.*

- Index = short one-line pointers only ("API style rules → `docs/api-style.md`").
- The detail moves to its own file (`docs/…`) or a skill; nothing is deleted, only routed.
- Rationale: the file is re-injected into *every* session and competes for attention —
  every line saved is saved on every future session (tokens + credits + accuracy).
- Mark it `Model: judgment` (deciding what routes where) but note the mechanical half
  (writing the pointer lines, creating the target files) is Haiku-safe.

This item is only skipped if the file is already a lean index.

---

## A. Context budget — the always-loaded tax

Root: an LLM call is stateless; `CLAUDE.md` + auto-memory are the only things re-injected
every session; the context window is finite and shared — always-loaded content dilutes
the model's attention.

| # | Check | Threshold / method | Sev |
|---|---|---|---|
| A1 | `~/.claude/CLAUDE.md` length | > 200 lines over budget; > 300 = HIGH | MED–HIGH |
| A2 | `memory/MEMORY.md` length | > 120 lines — it is an index, keep it lean | MED |
| A3 | Individual memory file | > ~40 lines, holds >1 fact, or carries transient state ("pending", "BLOCKED", dated changelog) | MED |
| A4 | Situational content inline in CLAUDE.md / a memory | style guides, long workflows, ref tables needed only for *some* tasks → route out + pointer (**route, never delete**) | MED |
| A5 | Stale reference | every path / skill name / flag / tool named in CLAUDE.md + memories — verify it exists; dead ref misleads every session | HIGH |
| A6 | Duplication | same fact in CLAUDE.md and a memory, or across memories; inconsistent name conventions | LOW |
| A7 | Filler | lines restating model defaults / obvious behaviour — pure tax | LOW |

## B. MCP servers — silent context tax

Root: MCP is a capability axis; each enabled server loads tool defs into context;
`/compact` can't reclaim it. Unused servers are pure overhead every session.

| # | Check | Method | Sev |
|---|---|---|---|
| B1 | Count enabled servers | `.mcp.json`, `settings*.json`, `~/.claude.json` `mcpServers` / `enabledMcpjsonServers` | — |
| B2 | Unused servers | each `mcp__<server>__` prefix vs `analyze.py tools --days 60`; 0 calls in 60d → disable | MED |
| B3 | Large eager-loading server used rarely | worst offender for the budget | MED |
| B4 | Redundant with a built-in | e.g. filesystem MCP over Read/Edit/Glob | LOW |

## C. Delegation & model choice

Root (Node A): a subagent is a fresh separate invocation with its own window → isolation,
parallelism, *and* per-agent model choice. Bulk/mechanical work (huge reads, scraping, log
triage, OCR) belongs in a Haiku subagent; the expensive model stays on the main thread for
reasoning. Isolation ≠ capability — a subagent gets no tools/MCP unless granted.

| # | Check | Method | Sev |
|---|---|---|---|
| C1 | Main-thread bulk work | `analyze.py sessions`, then `render` the biggest — main thread ingesting large files / many results / vision OCR that a Haiku subagent should have absorbed | MED |
| C2 | Grunt agent not on Haiku | any `~/.claude/agents/*.md` doing mechanical work without `model: haiku` | LOW |
| C3 | Over-broad agent tools | agent with `tools: *` that only needs read tools | LOW |
| C4 | Repeated manual workflow | `analyze.py prompts --days 60` — same multi-step ask typed repeatedly → skill candidate | MED |
| C5 | Haiku share of spend | `analyze.py cost` by model — Haiku ~0% while bulk work happens → delegation not used | MED |

## D. Skills hygiene

Root: a skill is disk content loaded **on demand** — long is fine; the `description:` is
load-bearing, a vague one never triggers.

| # | Check | Threshold | Sev |
|---|---|---|---|
| D1 | Oversized `SKILL.md` | > 500 lines, no `references/` folder holding the detail | MED |
| D2 | Weak `description:` | no trigger phrases / no "use when…" | MED |
| D3 | Disabled skill still needed | `settings.json` `skillOverrides` = `off` but its tools are still used a lot → re-enable or delete | MED |
| D4 | Overlap | two skills matching the same request | LOW |
| D5 | Orphan files | `references/`, `scripts/` not mentioned by the `SKILL.md` | LOW |

## E. Hooks & determinism

Root: a hook is a deterministic if-this-then-that firing outside the model — use it for
anything that must happen every time; a CLAUDE.md instruction is only *usually* obeyed.

| # | Check | Method | Sev |
|---|---|---|---|
| E1 | Hook scripts resolve | every `command` path in `settings*.json` hooks exists | HIGH |
| E2 | Hook failures in the wild | grep recent sessions for hook error / non-zero-exit lines | MED |
| E3 | "Always" rule stuck in CLAUDE.md | "always run X after editing" → belongs in a PostToolUse hook | LOW |

## F. settings.json & safety nets

Root: prevention (permission modes / classifier) and undo (git checkpoints) are two halves
of one defence; losing both at once compounds risk.

| # | Check | Method | Sev |
|---|---|---|---|
| F1 | `defaultMode` | `bypassPermissions` / `dontAsk` globally, esp. with no git repo at cwd | HIGH |
| F2 | `autoMode.allow` / `permissions.allow` hygiene | broad entries (`Bash(*)`, `Bash(git add *)`, `Bash(python:*)`); stale one-off allows | MED |
| F3 | `effortLevel` permanently high | `high`/`xhigh` default burns tokens on trivial turns | LOW |
| F4 | Model default | note it; flag if pinned to the priciest tier for everyday work | LOW |
| F5 | Duplicate / legacy keys | e.g. `voice.enabled` and `voiceEnabled` | LOW |

## G. Usage / credit rollup (report section, not graded)

Run and **summarise** — never paste raw tables:

- `analyze.py cost --days 30` — total est. spend, split by model. Call out low Haiku share
  or one project dominating.
- `analyze.py tools --days 30` — tool-call distribution; high Read/Grep hints at missing
  delegation.
- `analyze.py sessions --days 14` — flag very long single sessions (no `/clear`, repeated
  `/compact`, "ran out of context").
- `analyze.py prompts --days 30 --top 40` — cluster repeated asks → skill candidates.

`analyze-sessions` may be `off` in `skillOverrides`; call the script directly:
`python "~/.claude\skills\analyze-sessions\scripts\analyze.py" <cmd>` — the
override only blocks model-invocation of the skill, not the script. Try `py -3` if `python`
is missing.

---

## Required output

```
# Claude Code checkup — <date>

## Tier chart
| Area | Grade | One-line verdict |
|------|-------|------------------|
| A Context budget | B | ... |
| ... | | |
| **OVERALL** | **C** | dragged down by C — delegation |

## Remediation plan  (ranked; #1 is always the index transform if any always-loaded file is oversized)
| # | Area | Now | Target | Action | Model | Effort | Risk |
|---|------|-----|--------|--------|-------|--------|------|
| 1 | A | B | A | Split MEMORY.md: keep 1-line pointers, move Kairo changelog to docs/kairo-log.md | judgment | 15 min | low |
| 2 | F | F | A | settings.json:12 hook path `hooks/foo.py` does not exist — remove or restore | mechanical | 2 min | low |

## Usage snapshot
- short bullets, no raw tables

## Already good
- short factual bullets — what NOT to touch
```

`Model` column: `mechanical` (Haiku-safe) or `judgment` (needs Sonnet). Keep the whole
report under ~150 lines. Rank by severity, then effort. Never invent a finding to fill a
section — "nothing to fix" is a valid, good result.

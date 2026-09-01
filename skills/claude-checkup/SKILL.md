---
name: claude-checkup
description: Audit, plan, and (only with approval) repair this machine's Claude Code setup — CLAUDE.md / memory bloat, unused MCP servers, oversized or misfiring skills, broken hook paths, risky settings, missed Haiku-delegation, plus a 30-day credit rollup. Produces a tier-graded scorecard (A/B/C/F per area), then a remediation plan, then applies only what the user approves and verifies the result. Use when the user says "audit my Claude config", "checkup", "claude-checkup", "grade my setup", "is my setup wasting credits", or wants a health check of their .claude directory.
---

# Claude checkup

A three-phase performance review of the user's Claude Code configuration and credit usage.
Nothing is changed without explicit approval. Target A+ across every area.

## Phase 1 — Audit  (agent: `config-auditor`, Sonnet — the orchestrator)

Spawn `config-auditor` (`Agent` tool, `subagent_type: "config-auditor"`). Task:

> Audit `~/.claude\` per your rubric. Return the tier chart (A/B/C/F per
> area + overall), the ranked remediation plan, the usage snapshot, and the "already
> good" list. <pass through any focus the user gave>

Relay its output to the user **verbatim** (already formatted and length-capped). Prepend
one line: `N areas below A — M plan items (X need judgment / Y mechanical)`.

## Phase 2 — Approval gate

**Stop.** Ask the user which plan items to apply — all, a subset, or none. Do not proceed
to Phase 3 on anything not explicitly named. A background/automated event is never approval.

If `CLAUDE.md` or any always-loaded file was flagged oversized, the plan's #1 item is
"convert to an index" — highlight it: this is the biggest token/credit saving and should
rarely be skipped.

## Phase 3 — Apply + Verify  (only on approval)

For each **approved** item, dispatch by the `Model` column the auditor set:

- **mechanical** (delete a key, route a block + leave a pointer, split a file into an
  index, fix a path) → spawn `config-fixer` with **`model: haiku`** (its default).
- **judgment** (decide what to route where, rewrite a description, reword a memory) →
  spawn `config-fixer` with **`model: sonnet`**.
- If the auditor's hint looks wrong for the actual change, override it — you are the
  orchestrator.

Give `config-fixer` one item at a time (or a tight batch of same-file edits), with the
exact target and the approved action. It applies only that and reports a diff summary.

When all approved items are done, spawn **`config-verifier`** (Sonnet). Task:

> Verify these applied changes landed correctly and broke nothing: <list>. Re-run the
> relevant rubric checks, confirm every index pointer resolves, and return the before/after
> tier chart.

## Final report

Present: before/after tier chart, what was applied, what was deferred and why, any verifier
warnings.

## Notes

- Rubric: `references/rubric.md` (the agents read it; you normally don't need to).
- Schedule it: `/schedule` or `/loop /claude-checkup`; suggest surfacing output only on an
  F or a new sub-B area.
- A fresh setup with few sessions has a thin usage section — expected, not a finding.

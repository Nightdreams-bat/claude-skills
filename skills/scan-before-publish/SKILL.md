---
name: scan-before-publish
description: Scan a repo for leaked secrets (API keys, tokens, DB URLs, credentials) with ggshield before pushing, open-sourcing, or sharing a build. Use whenever the user is about to publish, push, release, or hand off code — or says "scan before publish", "check for secrets", "/scan-before-publish".
---

# scan before publish

Runs GitGuardian's `ggshield` over a repo's **git history** and **working tree**
and reports any leaked secrets with file + line, before the code goes anywhere
public.

On this machine ggshield is installed via `pip --user`. The working command name
is **`ggshield-py`** (the plain `ggshield` binary is missing its bundle). If
`ggshield-py` is not found, run `python -m ggshield` instead.

## Steps

1. **Pick the target repo.** Default to the current directory; if the user named
   a project, `cd` there. Confirm it's a git repo (`git rev-parse --is-inside-work-tree`).

2. **Check auth once.** Run `ggshield-py api-status`. If it reports no token /
   not authenticated, stop and tell the user to run:
   ```
   ! ggshield-py auth login
   ```
   (or `! ggshield-py auth login --method oob` if the browser flow fails). The
   token is stored globally, so this is a one-time step.

3. **Scan git history:**
   ```
   ggshield-py secret scan repo .
   ```

4. **Scan the working tree** (catches gitignored / uncommitted files on disk).
   It prompts to confirm when >20 files; pipe `yes` to auto-confirm:
   ```
   yes | ggshield-py secret scan path -r .
   ```

5. **Report.**
   - Clean → say so plainly: history and working tree both clean, safe to publish.
   - Findings → list each: secret type, file, line, and whether it's in committed
     history (harder to fix — needs history rewrite or key rotation) or only in a
     working-tree file (just remove / gitignore it). Do **not** paste the secret
     value itself. Recommend rotating any real key that was ever committed.

## Notes

- `.gitignore`'d files (`config.json`, `client_secret.json`, `clients.xlsx`,
  logs) are expected to contain secrets — that's fine as long as the history
  scan shows they were never committed. Call that out explicitly.
- To make ggshield run automatically on every commit in a repo:
  `ggshield-py install -m local -t pre-commit`
- Exit code 1 from a scan means secrets were found; exit 0 means clean.

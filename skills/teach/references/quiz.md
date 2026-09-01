# Quiz — porting the graded-question extension

The original system had a dedicated `quiz` tool: the learner picked an option and got instant ✓/✗, the correct answer, and an explanation, all inside the tool UI. Claude Code has no such tool. `AskUserQuestion` collects the answer but **does not grade it**.

So the grading is your job, and it is mandatory. **A quiz that isn't graded in your very next message is not a quiz — it's a survey, and it teaches nothing.**

## The two shapes, and never confuse them

| | **Quiz** | **Open fork** |
|---|---|---|
| Has a correct answer | Yes | No |
| Purpose | Locate the edge / confirm a node landed | Learn a preference or direction |
| Example | "What does a TCP sequence number identify?" | "Want the math derivation or the intuition first?" |
| After the answer | **Grade it: ✓/✗, correct answer, explanation** | Just act on it; never grade |
| Tracked in the vault | Yes — every answer updates the concept file | No |

If a question has a definite right answer, it is a quiz, even when you're using it Socratically to let them discover something. Gradable-and-Socratic is the normal case, not a contradiction.

## Presenting a quiz

Use `AskUserQuestion`:

- **1–4 questions per call.** During Phase 1a probing, prefer 1–2 per call so you can adapt difficulty to the last answer — binary-searching the edge is impossible if you fire four fixed questions at once. For a broad diagnostic sweep, 4 is fine.
- 4 options each, single-select (`multiSelect: false`).
- `header`: max 12 chars, e.g. `Q1. Packets`.
- **Never** use "(Recommended)" on any option.
- **Randomize the correct answer's position.** Never always first or last.

## Writing options — a construction procedure

The usual advice is "keep the options even." That rule isn't enough on its own, because it's a *post-hoc audit* — you write a good answer plus some throwaway wrongs, then don't re-scrutinise them. The tell is baked in before any check runs. So don't audit afterwards; **build the options so evenness is automatic**:

1. **Every option is a bare claim — no justification anywhere.** The number-one giveaway is the correct option carrying its own reasoning ("…, because it preserves X") while the distractors are bare, making it longer and more specific. Put *zero* "why" in any option; all reasoning goes in the explanation you give *after* they answer.
2. **Write the correct claim first, then mutate it into each distractor.** Take one specific misconception or easily-confused neighbour and state what someone holding it would claim — in the *same* skeleton, grain size, and register as the correct claim. Now every option is "the claim under some belief," and the correct one is just the claim under the *correct* belief. Parallelism falls out by construction instead of being policed.
3. **Each distractor must be a real error they might actually make** (so which one they pick is diagnostic), yet unambiguously wrong on the intended reading — tempting, not tricky.
4. **No asymmetric bolding.** Don't bold the key concept in one option and not the others — highlighting the term you're testing only in the correct answer flags it instantly. Either bold nothing, or bold the parallel term in every option.
5. **Zero hints in the `description` field.** The description explains what the option *means*, never whether it's right.
   - BAD: `label: "stderr"` / `description: "Error stream Cloud Run uses for error classification"`
   - GOOD: `label: "stderr"` / `description: "Standard error stream"`
6. **Don't hint in the question stem either.** BAD: "Which error stream does `error()` use?" GOOD: "Where does `error()` output go?"

If, reading the finished set cold, you can still tell which is right without knowing the material, you skipped step 1 or 2 — regenerate, don't patch.

## Question types to draw from

1. **Factual recall** — "What status code is returned when…?"
2. **Conceptual understanding** — "Why does the system use X?"
3. **Behavioural prediction** — "What happens when X fails?"
4. **Comparison/distinction** — "What's the difference between X and Y?"
5. **Debugging scenario** — "Given this error, what's the most likely cause?"

Difficulty mix: diagnostic sweep 40% easy / 40% medium / 20% hard; weak-area drill 30% medium / 70% hard; edge-hunting (Phase 1a) is adaptive by definition — ignore the mix and binary-search instead.

## Grading — your next message, always

Immediately after the answer comes back:

1. **Result line per question**: ✓ or ✗, their answer, and the correct answer if they missed.
2. **Explanation** — for a miss, explain *what belief would produce that specific wrong option* and why it fails, not just what the right answer is. The distractor they picked is diagnostic; use it. For a hit, one line confirming *why* it's right, so the connection gets reinforced rather than just the fact.
3. If they missed, **the node is not solid.** Do not build on it. Go back, re-motivate, re-establish, re-check.
4. **Write it to the concept tracker** — see `vault.md`.

For a multi-question round, a small table reads best:

```markdown
| # | Question | Your answer | Correct | Result |
|---|----------|-------------|---------|--------|
| 1 | ...      | ...         | ...     | ✓      |
```

## Drilling a concept they already missed

Do **not** repeat the exact same question — test the same underlying knowledge from a different angle, in a new context. If they confused "400 vs 422", give a fresh scenario where they must pick the right one, not the same definition question again.

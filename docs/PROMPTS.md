# PROMPTS.md — Session Kickoff Prompts

*Copy-paste these verbatim; fill only `<N>` and `<slug>`. Never add task
instructions here or in the prompt itself — requirements belong in SPEC.md or
TRACKER.md, where the next session can see them.*

---

## 1 — New sprint

```
Run /agent-entry. We're starting Sprint S<N>.

Create branch sprint/<N>-<slug>, and give me your PLAN for the first bite
of S<N> — nibble 1 only: the exact schematic edits with citations. Change
no files until I approve.

Remember: I close KiCad before you edit, every bite ends with ERC + a net
diff, I do the KiCad look, and this sprint isn't done until I've run its
demo from the TRACKER and it passes.
```

## 2 — Resume mid-sprint

```
Run /agent-entry. We're mid-Sprint S<N> on branch sprint/<N>-<slug>.
Check the branch diff against the TRACKER state and the top DEV_LOG entry,
tell me exactly where the last session stopped and which nibble we're in,
and wait for my go before continuing.
```

## 3 — Sprint close-out (demo already passed)

```
Sprint S<N> demo passed on my end. Close it out: mark S<N> done in
TRACKER.md, append the DEV_LOG entry, add the ERC/net-check row and any
decisions to DESIGN.md, open the PR with the demo commands in the
description, and show me the diff of all doc changes before committing.
```

## 4 — Capture a task without acting on it

```
Run /capture-task: <one-line description>. Size it, place it (current
sprint / later sprint / icebox), show me the TRACKER diff, and then
return to the current bite — do not start work on it.
```

## 5 — Quality Engineer review

```
Spawn the Quality Engineer review of PR #<N> (<sprint>) as a separate session
(task chip), never a sub-agent; later rounds go to the same session. Put your
session id in every request so the QE sends its report back to you. Save each
report to docs/design-review/qe/<sprint>.md, post it on the PR, fix anything it
hands back and send the next round until it approves; then tell me the verdict.
Don't merge.
```

## 6 — Layout question (no edits)

```
Run /agent-entry, read-only. Layout question: <question>. Answer from the
schematic, SPEC and datasheets with citations. Don't edit any file.
```

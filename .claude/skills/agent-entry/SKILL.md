---
name: agent-entry
description: Session-start ritual for this repo. Run at the start of every session before any other work — reads the tracker and docs, reports where things stand, and waits for Nick's go.
---

# /agent-entry

1. Read `docs/TRACKER.md` cover to cover, including the Rules for Agents.
2. Skim `docs/SPEC.md` and `docs/DESIGN.md`. If the current sprint is S3,
   also read `docs/POWER_PATH.md`.
3. Read the top 3 entries of `docs/DEV_LOG.md`.
4. Run `git status` and `git branch --show-current`; note any uncommitted
   changes and whether the branch matches the sprint.
5. Report back in five lines or fewer:
   - current sprint and its state
   - which bite and nibble we're in (per TRACKER and the top DEV_LOG entry)
   - the single next bite you propose
   - open questions blocking it, if any
   - "Please close KiCad before I edit" if the next step edits project files
6. Wait for Nick's go. Change no files during this ritual.

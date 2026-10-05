# DEV_LOG.md — Session Log

*Newest entries on top. One entry per working session. Short: what changed,
what broke, what's next.*

---

## Entry template

```
## YYYY-MM-DD — Sprint Sn — <one-line summary>
**Branch:** sprint/n-slug
**Files touched:** <sheets / docs>
**ERC:** <n errors / n warnings>  ·  **Net diff:** <clean | n changed — intended?>
**Done:**  <bullets>
**Broke/surprised us:** <bullets or "nothing">
**Next:** <the single next bite>
```

---

## 2026-10-05 — Sprint S0 — Net check built; baseline recorded

**Branch:** sprint/0-net-check
**Files touched:** tools/ (new), .gitignore, docs/design-review/netcheck.md, docs/*, checklist HTML
**ERC:** 90 errors / 578 warnings  ·  **Net diff:** 42/68 matched, 26 opens, 0 shorts
**Done:**
- `tools/netcheck.py` (stdlib, 5 unit tests) compares schematic connectivity
  with the mote copper; `tools/check.sh` runs ERC + netlist + PDF + netcheck
- Baseline in DESIGN.md; every open listed in `docs/design-review/netcheck.md`
**Broke/surprised us:**
- The junction fix isn't complete: 26 copper nets are still split, mostly
  single pins on wire midpoints (TP20/21/22, C13/C14, D4/D5 pin 1, R1 pin 1, …)
- The untouched reference schematic has 38 opens against its own copper, so
  this is import damage
- The probe's 48/74 became 42/68 in the tool: same opens, minus 6 trivially
  matched single-pin nets
**Next:** S0 demo passed (Nick, 2026-10-05) → S0 done. Next: S1, fixing the 26 opens (plan nibble).

## 2026-10-04 — Sprint S0 — Project renamed, junk untracked, rating defined

**Branch:** sprint/0-repo-baseline
**Files touched:** project folder (rename only), 58 files untracked, docs/*
**ERC:** 90 errors / 578 warnings, the same before and after  ·  **Net diff:** clean (library path only)
**Done:**
- S0.1: `_002` → `nereus_Pi_shield_ADIN2111/`; the stray `.kicad_pro` was byte-identical
- S0.2: `git rm --cached` for everything `.gitignore` covers
- Recorded Nick's decisions: ~50 W absolute max at 24 V (D8); potted, so newly
  sourced parts can't be electrolytics or PPTCs, while vetted Sofar parts stay
  as-is (D9, SPEC constraint 8)
- Bourns SRF1260 datasheet figures added to POWER_PATH; this explains the mote's 20 W
- New `docs/SOFAR_QUESTIONS.md` (Q1 e-fuse, Q2–Q4 moved from SPEC, Q5 MSD1514/damping)
- `pi-shield-checklist.html` rebuilt to mirror TRACKER: S0–S6, Sofar questions,
  status panel; finished work marked "✓ in repo" in the data (D2 revised;
  TRACKER rule 6 now requires syncing it every PR)
**Broke/surprised us:**
- kicad-cli ERC names different example labels from run to run; compare counts, not text
- No fuse or e-fuse anywhere on the through path (Nick remembered one; asked Sofar, Q1)
- The FPF2700 datasheet link on onsemi is dead
**Next:** S0.3, the net-check method.

## 2026-10-04 — Pre-work — Docs fitted to the KiCad project

**Branch:** claude/kicad-docs-setup-19be00
**Files touched:** CLAUDE.md, README.md, .gitignore, docs/*, .claude/skills/*, checklist banner
**ERC:** not run (no schematic edits)  ·  **Net diff:** n/a
**Done:**
- Templates filled for schematic capture; sprint ladder S0–S6 built from the
  checklist, plus the new S3 (50 W power path)
- `docs/POWER_PATH.md` seeded from Evan's two Sofar references
- `/agent-entry` and `/capture-task` skills added
**Broke/surprised us:**
- Live PoDL inductors are SRF1260-101M (~20 W), so 50 W touches the whole power path
- The Processor and USB sheets are orphan files, not part of the hierarchy
- MSD1514 (Sofar's 50 W pick) is 15.5 × 15.5 × 14.2 mm, which is tight on a Pi Zero board
**Next:** S0.1, plan nibble — Nick gate.

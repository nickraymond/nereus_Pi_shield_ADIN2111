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
